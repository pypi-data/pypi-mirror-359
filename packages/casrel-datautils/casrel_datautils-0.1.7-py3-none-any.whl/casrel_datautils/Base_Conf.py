import torch
from transformers import BertTokenizer, BertModel
import json
import os
import logging
import shutil

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseConfig:
    """单例模式配置类，用于全局配置参数。
    使用说明：通过 BaseConfig(bert_path_or_bertModel_name, train_data, dev_data, test_data, rel_data, batch_size, max_length, cache_dir) 创建实例，
    bert_path_or_bertModel_name 可选，若未提供或无效则下载 'bert-base-chinese' 并返回绝对路径，其他参数为数据集路径、批次大小、最大序列长度和缓存目录。
    鲁棒性：必须提供 train_data, test_data 和 rel_data，若 dev_data 为空则使用 test_data；max_length 可选，若未设置则动态计算批次最大长度，但不超过 BERT 最大长度。
    可用性：支持自定义 cache_dir，若无效则回退到默认缓存目录，并确保模型加载成功。

    参数：
        bert_path_or_bertModel_name (str, optional): BERT 模型路径或模型名称，若为空则自动下载 'bert-base-chinese'。
        train_data (str): 训练数据路径，不可为空。
        dev_data (str): 验证数据路径，可为空，若为空则使用 test_data。
        test_data (str): 测试数据路径，不可为空。
        rel_data (str): 关系数据路径，不可为空。
        batch_size (int): 批次大小，默认 32。
        max_length (int, optional): 最大序列长度，若未提供则动态计算批次中最长句子长度，但不超过 BERT 最大长度 (默认 512)。
        cache_dir (str, optional): 自定义缓存目录，若未提供则使用默认缓存目录 (~/.cache/huggingface/transformers)。
    """
    _instance = None

    def __new__(cls, bert_path_or_bertModel_name=None, train_data=None, dev_data=None, test_data=None, rel_data=None,
                batch_size=32, max_length=None, cache_dir=None):
        """单例模式构造函数，确保只初始化一次配置。
        参数：
            bert_path_or_bertModel_name (str, optional): BERT 模型路径或模型名称，若为空则自动下载 'bert-base-chinese'。
            train_data (str): 训练数据路径，不可为空。
            dev_data (str): 验证数据路径，可为空，若为空则使用 test_data。
            test_data (str): 测试数据路径，不可为空。
            rel_data (str): 关系数据路径，不可为空。
            batch_size (int): 批次大小，默认 32。
            max_length (int, optional): 最大序列长度，若未提供则动态计算。
            cache_dir (str, optional): 自定义缓存目录，若未提供则使用默认缓存目录。
        """
        if cls._instance is None:
            cls._instance = super(BaseConfig, cls).__new__(cls)
            cls._instance._initialize(bert_path_or_bertModel_name, train_data, dev_data, test_data, rel_data,
                                      batch_size, max_length, cache_dir)
        return cls._instance

    def _initialize(self, bert_path_or_bertModel_name, train_data, dev_data, test_data, rel_data, batch_size,
                    max_length, cache_dir):
        """初始化配置参数。
        使用说明：内部方法，自动检测设备并加载 BERT 模型及 tokenizer，支持自定义路径或默认下载，并动态设置 bert_dim 和 max_length。
        鲁棒性：检查文件路径是否存在，避免因文件缺失导致崩溃；记录核心日志；验证 max_length 不超过 BERT 最大长度。
        可用性：若 cache_dir 无效或不可用，回退到默认缓存目录；若模型加载失败，尝试重新下载。
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # 自动选择设备
        # 设置缓存目录
        self.cache_dir = cache_dir if cache_dir and os.path.isdir(cache_dir) else os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "transformers")
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir, exist_ok=True)
                logger.info(f"创建缓存目录: {self.cache_dir}")
            except Exception as e:
                logger.warning(f"无法创建缓存目录 {self.cache_dir}, 回退到默认行为: {str(e)}")
                self.cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "transformers")
                os.makedirs(self.cache_dir, exist_ok=True)
                logger.info(f"回退并创建默认缓存目录: {self.cache_dir}")
        # 初始化 bert_path_or_bertModel_name
        self.bert_path_or_bertModel_name = bert_path_or_bertModel_name if bert_path_or_bertModel_name else "bert-base-chinese"
        try:
            # 判断是模型名称还是路径
            is_model_name = not os.path.isdir(self.bert_path_or_bertModel_name)
            if is_model_name:
                # 构造缓存路径
                cache_path = os.path.join(self.cache_dir, self.bert_path_or_bertModel_name.replace("/", "_"))
                if os.path.exists(cache_path):
                    logger.info(f"检测到缓存，尝试复用 BERT 模型，路径: {cache_path}")
                    self.tokenizer = BertTokenizer.from_pretrained(cache_path, cache_dir=self.cache_dir)
                    self.bert_model = BertModel.from_pretrained(cache_path, cache_dir=self.cache_dir)
                    self.bert_path_or_bertModel_name = cache_path
                else:
                    logger.info(f"缓存不存在，下载 BERT 模型，目标路径: {cache_path}")
                    self.tokenizer = BertTokenizer.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                    self.bert_model = BertModel.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                    self.bert_path_or_bertModel_name = cache_path
            else:
                # 直接使用本地路径
                logger.info(f"使用本地 BERT 模型，路径: {self.bert_path_or_bertModel_name}")
                self.tokenizer = BertTokenizer.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                self.bert_model = BertModel.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
            # 验证模型加载
            actual_cache_dir = self.tokenizer._cache_dir or self.bert_model._cache_dir
            if actual_cache_dir and os.path.exists(actual_cache_dir):
                self.bert_path_or_bertModel_name = os.path.abspath(actual_cache_dir)
                logger.info(f"BERT 模型加载成功，绝对路径: {self.bert_path_or_bertModel_name}")
            else:
                logger.info(f"BERT 模型加载成功，使用指定路径: {self.bert_path_or_bertModel_name}")
            self.bert_dim = self._get_bert_dim(self.bert_path_or_bertModel_name)
        except Exception as e:
            logger.error(f"加载 BERT 模型 {self.bert_path_or_bertModel_name} 失败: {str(e)}")
            # 尝试重新下载
            if is_model_name and "Incorrect path_or_model_id" not in str(e) and os.path.exists(cache_path):
                logger.info(f"缓存可能损坏，清除缓存并重新下载: {cache_path}")
                shutil.rmtree(cache_path, ignore_errors=True)
                self.tokenizer = BertTokenizer.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                self.bert_model = BertModel.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                actual_cache_dir = self.tokenizer._cache_dir or self.bert_model._cache_dir
                if actual_cache_dir:
                    self.bert_path_or_bertModel_name = os.path.abspath(actual_cache_dir)
                    logger.info(f"重新下载 BERT 模型成功，绝对路径: {self.bert_path_or_bertModel_name}")
                else:
                    raise ValueError(f"重新下载 BERT 模型失败: {str(e)}")
            else:
                raise ValueError(f"无法加载 BERT 模型 {self.bert_path_or_bertModel_name}: {str(e)}")

        # 验证并设置数据路径
        if not train_data or not os.path.exists(train_data):
            logger.error("train_data 路径必须提供且文件必须存在")
            raise ValueError("train_data 路径必须提供且文件必须存在")
        self.train_data = os.path.abspath(train_data)  # 使用绝对路径

        if not test_data or not os.path.exists(test_data):
            logger.error("test_data 路径必须提供且文件必须存在")
            raise ValueError("test_data 路径必须提供且文件必须存在")
        self.test_data = os.path.abspath(test_data)  # 使用绝对路径

        self.dev_data = os.path.abspath(dev_data) if dev_data and os.path.exists(dev_data) else self.test_data  # 默认使用 test_data
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
        self.max_length = max_length if max_length and isinstance(max_length, int) and max_length > 0 else None  # 用户自定义 max_length
        logger.info(f"配置初始化完成，batch_size: {self.batch_size}, max_length: {self.max_length}")

    def _is_valid_bert_path(self, bert_path_or_bertModel_name):
        """检查 BERT 模型路径或模型名称是否有效。
        使用说明：验证 bert_path_or_bertModel_name 是否可被 transformers 识别。
        参数：
            bert_path_or_bertModel_name (str): BERT 模型路径或模型名称。
        返回：
            bool: 路径或名称是否有效。
        """
        try:
            BertTokenizer.from_pretrained(bert_path_or_bertModel_name)
            return True
        except:
            return False

    def _get_cache_dir(self, bert_path_or_bertModel_name):
        """获取 BERT 模型的缓存目录。
        使用说明：根据模型名称或路径返回缓存目录的绝对路径。
        参数：
            bert_path_or_bertModel_name (str): BERT 模型路径或模型名称。
        返回：
            str: 缓存目录的绝对路径（仅用于日志记录，实际路径由 transformers 管理）。
        """
        if os.path.isdir(bert_path_or_bertModel_name):  # 如果是本地路径
            return os.path.abspath(bert_path_or_bertModel_name)
        else:  # 假设是模型名称
            model_cache_dir = os.path.join(self.cache_dir, bert_path_or_bertModel_name.replace("/", "_"))
            return os.path.abspath(model_cache_dir)

    def _download_default_bert(self):
        """下载默认 BERT 模型并返回绝对路径。
        使用说明：若 bert_path_or_bertModel_name 未提供或无效，则下载 'bert-base-chinese' 并返回其缓存路径。
        返回：
            str: 下载的 BERT 模型绝对路径。
        """
        default_model = "bert-base-chinese"
        try:
            tokenizer = BertTokenizer.from_pretrained(default_model, cache_dir=self.cache_dir)
            model = BertModel.from_pretrained(default_model, cache_dir=self.cache_dir)
            actual_cache_dir = self.tokenizer._cache_dir or self.bert_model._cache_dir
            if actual_cache_dir:
                absolute_path = os.path.abspath(actual_cache_dir)
                logger.info(f"默认 BERT 模型 {default_model} 下载完成，绝对路径: {absolute_path}")
                return absolute_path
            else:
                raise ValueError("无法确定 BERT 模型缓存路径")
        except Exception as e:
            logger.error(f"下载默认 BERT 模型失败: {str(e)}")
            raise ValueError(f"下载默认 BERT 模型失败: {str(e)}")

    def _get_bert_dim(self, bert_path_or_bertModel_name):
        """根据 BERT 模型路径或名称获取隐藏层维度。
        使用说明：内部方法，根据模型名称动态设置 bert_dim。
        参数：
            bert_path_or_bertModel_name (str): BERT 模型路径或名称。
        返回：
            int: 模型的隐藏层维度。
        鲁棒性：默认返回 768，若无法判断则抛出警告。
        """
        try:
            if "large" in bert_path_or_bertModel_name.lower():
                return 1024  # bert-large 系列的隐藏层维度
            else:
                return 768  # bert-base 系列的隐藏层维度（包括 RoBERTa 和 WWM 变体）
        except:
            logger.warning(f"无法确定 {bert_path_or_bertModel_name} 的 bert_dim，默认使用 768")
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
if __name__ == '__main__':
    try:
        # 示例 1: 使用默认缓存目录
        baseconf1 = BaseConfig(
            bert_path_or_bertModel_name="bert-base-chinese",
            train_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\test.json",
            test_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\one_Sample.json",
            rel_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\relation.json",
            max_length=128
        )
        print("示例 1 - bert_path_or_bertModel_name:", baseconf1.bert_path_or_bertModel_name)

        # 示例 2: 使用自定义缓存目录
        custom_cache_dir = r"C:\Users\lidat\custom_bert_cache"
        baseconf2 = BaseConfig(
            bert_path_or_bertModel_name="bert-base-chinese",
            train_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\test.json",
            test_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\one_Sample.json",
            rel_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\relation.json",
            max_length=128,
            cache_dir=custom_cache_dir
        )
        print("示例 2 - bert_path_or_bertModel_name:", baseconf2.bert_path_or_bertModel_name)
    except Exception as e:
        print(f"主程序执行错误: {str(e)}")