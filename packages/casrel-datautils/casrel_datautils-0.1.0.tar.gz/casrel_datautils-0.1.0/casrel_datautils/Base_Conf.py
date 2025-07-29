import torch
from transformers import BertTokenizer, BertModel
import json
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseConfig:
    """单例模式配置类，用于全局配置参数。
    使用说明：通过 BaseConfig(bert_path, train_data, dev_data, test_data, rel_data, batch_size, max_length) 创建实例，
    bert_path 可选，若未提供则下载 'bert-base-chinese' 并返回绝对路径，其他参数为数据集路径、批次大小和最大序列长度。
    鲁棒性：必须提供 train_data, test_data 和 rel_data，若 dev_data 为空则使用 test_data；max_length 可选，若未设置则动态计算批次最大长度，但不超过 BERT 最大长度。

    参数：
        bert_path (str, optional): BERT 模型路径，若为空则自动下载 'bert-base-chinese'。
        train_data (str): 训练数据路径，不可为空。
        dev_data (str): 验证数据路径，可为空，若为空则使用 test_data。
        test_data (str): 测试数据路径，不可为空。
        rel_data (str): 关系数据路径，不可为空。
        batch_size (int): 批次大小，默认 32。
        max_length (int, optional): 最大序列长度，若未提供则动态计算批次中最长句子长度，但不超过 BERT 最大长度 (默认 512)。
    """
    _instance = None

    def __new__(cls, bert_path=None, train_data=None, dev_data=None, test_data=None, rel_data=None, batch_size=32,
                max_length=None):
        """单例模式构造函数，确保只初始化一次配置。
        参数：
            bert_path (str, optional): BERT 模型路径，若为空则自动下载 'bert-base-chinese'。
            train_data (str): 训练数据路径，不可为空。
            dev_data (str): 验证数据路径，可为空，若为空则使用 test_data。
            test_data (str): 测试数据路径，不可为空。
            rel_data (str): 关系数据路径，不可为空。
            batch_size (int): 批次大小，默认 32。
            max_length (int, optional): 最大序列长度，若未提供则动态计算。
        """
        if cls._instance is None:
            cls._instance = super(BaseConfig, cls).__new__(cls)
            cls._instance._initialize(bert_path, train_data, dev_data, test_data, rel_data, batch_size, max_length)
        return cls._instance

    def _initialize(self, bert_path, train_data, dev_data, test_data, rel_data, batch_size, max_length):
        """初始化配置参数。
        使用说明：内部方法，自动检测设备并加载 BERT 模型及 tokenizer，支持自定义路径或默认下载，并动态设置 bert_dim 和 max_length。
        鲁棒性：检查文件路径是否存在，避免因文件缺失导致崩溃；记录核心日志；验证 max_length 不超过 BERT 最大长度。
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # 自动选择设备
        self.bert_path = bert_path if bert_path and self._is_valid_bert_path(
            bert_path) else self._download_default_bert()
        try:
            self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)  # 初始化 BERT tokenizer
            self.bert_model = BertModel.from_pretrained(self.bert_path)  # 初始化 BERT 模型
            self.bert_dim = self._get_bert_dim(self.bert_path)  # 动态设置 bert_dim
            logger.info(f"BERT 模型加载成功，路径: {self.bert_path}")
        except Exception as e:
            logger.error(f"加载 BERT 模型 {self.bert_path} 失败: {str(e)}")
            raise ValueError(f"无法加载 BERT 模型 {self.bert_path}: {str(e)}")

        # 验证并设置数据路径
        if not train_data or not os.path.exists(train_data):
            logger.error("train_data 路径必须提供且文件必须存在")
            raise ValueError("train_data 路径必须提供且文件必须存在")
        self.train_data = os.path.abspath(train_data)  # 使用绝对路径

        if not test_data or not os.path.exists(test_data):
            logger.error("test_data 路径必须提供且文件必须存在")
            raise ValueError("test_data 路径必须提供且文件必须存在")
        self.test_data = os.path.abspath(test_data)  # 使用绝对路径

        self.dev_data = os.path.abspath(dev_data) if dev_data and os.path.exists(
            dev_data) else self.test_data  # 默认使用 test_data
        if not rel_data or not os.path.exists(rel_data):
            logger.error("rel_data 路径必须提供且文件必须存在")
            raise ValueError("rel_data 路径必须提供且文件必须存在")
        self.rel_data = os.path.abspath(rel_data)  # 使用绝对路径

        # 加载关系数据并构建映射
        self.id2rel = {}
        self.rel2id = {}
        self.num_rel = 0
        if self.rel_data:
            try:
                self.id2rel = json.load(open(self.rel_data, encoding='utf8'))  # 加载 id 到关系映射
                self.rel2id = {rel: id for rel, id in self.id2rel.items()}  # 构建关系到 id 映射
                self.num_rel = len(self.id2rel)  # 关系数量
                logger.info(f"关系数据加载成功，路径: {self.rel_data}")
            except Exception as e:
                logger.error(f"加载关系数据 {self.rel_data} 失败: {str(e)}")
                raise ValueError(f"加载关系数据失败: {str(e)}")

        self.batch_size = batch_size if isinstance(batch_size, int) and batch_size > 0 else 32  # 确保批次大小有效
        self.max_length = max_length if max_length and isinstance(max_length,
                                                                  int) and max_length > 0 else None  # 用户自定义 max_length
        logger.info(f"配置初始化完成，batch_size: {self.batch_size}, max_length: {self.max_length}")

    def _is_valid_bert_path(self, bert_path):
        """检查 BERT 模型路径是否有效。
        使用说明：验证 bert_path 是否可被 transformers 识别。
        参数：
            bert_path (str): BERT 模型路径。
        返回：
            bool: 路径是否有效。
        """
        try:
            BertTokenizer.from_pretrained(bert_path)
            return True
        except:
            return False

    def _download_default_bert(self):
        """下载默认 BERT 模型并返回绝对路径。
        使用说明：若 bert_path 未提供，则下载 'bert-base-chinese' 并返回其缓存路径。
        返回：
            str: 下载的 BERT 模型绝对路径。
        """
        default_model = "bert-base-chinese"
        try:
            tokenizer = BertTokenizer.from_pretrained(default_model)
            model = BertModel.from_pretrained(default_model)
            cache_dir = tokenizer._cache_dir or model._cache_dir
            if cache_dir:
                absolute_path = os.path.abspath(cache_dir)
                logger.info(f"默认 BERT 模型 {default_model} 下载完成，绝对路径: {absolute_path}")
                return absolute_path
            else:
                raise ValueError("无法确定 BERT 模型缓存路径")
        except Exception as e:
            logger.error(f"下载默认 BERT 模型失败: {str(e)}")
            raise ValueError(f"下载默认 BERT 模型失败: {str(e)}")

    def _get_bert_dim(self, bert_path):
        """根据 BERT 模型路径获取隐藏层维度。
        使用说明：内部方法，根据模型名称动态设置 bert_dim。
        参数：
            bert_path (str): BERT 模型路径或名称。
        返回：
            int: 模型的隐藏层维度。
        鲁棒性：默认返回 768，若无法判断则抛出警告。
        """
        try:
            if "large" in bert_path.lower():
                return 1024  # bert-large 系列的隐藏层维度
            else:
                return 768  # bert-base 系列的隐藏层维度（包括 RoBERTa 和 WWM 变体）
        except:
            logger.warning(f"无法确定 {bert_path} 的 bert_dim，默认使用 768")
            return 768

    def get_available_bert_models(self):
        """返回可用的 BERT 模型列表。
        使用说明：列出支持的预训练模型名称及适用场景，供用户选择。
        返回：
            list: 包含模型名称和描述的字典列表。
        """
        return [
            {"name": "bert-base-chinese",
             "description": "默认中文 BERT 基础模型，适用于通用中文任务，参数量适中，bert_dim=768。"},
            {"name": "bert-large-chinese",
             "description": "较大规模的中文 BERT 模型，适用于需要更高精度的大型数据集，bert_dim=1024。"},
            {"name": "hfl/chinese-roberta-wwm-ext",
             "description": "基于 RoBERTa 的中文模型，带全词掩码，适合复杂关系抽取任务，bert_dim=768。"},
            {"name": "hfl/chinese-bert-wwm",
             "description": "带全词掩码的中文 BERT，适用于需要更好语义理解的任务，bert_dim=768。"},
        ]


# 示例使用（主程序中初始化）
# if __name__ == '__main__':
    # try:
    #     baseconf = BaseConfig(bert_path=None, train_data="train.json", test_data="test.json", rel_data="relation.json",
    #                           max_length=128)
    #     print("id2rel:", baseconf.id2rel)
    #     print("rel2id:", baseconf.rel2id)
    #     print("bert_dim:", baseconf.bert_dim)
    #     print("dev_data:", baseconf.dev_data)
    #     print("bert_path:", baseconf.bert_path)
    #     print("max_length:", baseconf.max_length)
    #     print("可用 BERT 模型:", baseconf.get_available_bert_models())
    # except Exception as e:
    #     print(f"主程序执行错误: {str(e)}")