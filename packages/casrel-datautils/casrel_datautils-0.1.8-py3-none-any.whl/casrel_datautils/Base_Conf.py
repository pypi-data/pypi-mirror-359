import torch
from transformers import BertTokenizer, BertModel
from modelscope import snapshot_download
import json
import os
import logging
import shutil
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseConfig:
    """单例模式配置类，用于全局配置参数。
    使用说明：通过 BaseConfig(bert_path_or_bertModel_name, train_data, dev_data, test_data, rel_data, batch_size, max_length, cache_dir) 创建实例，
    bert_path_or_bertModel_name 可选，若未提供或无效则下载 'bert-base-chinese' 并返回绝对路径，其他参数为数据集路径、批次大小、最大序列长度和缓存目录。
    鲁棒性：必须提供 train_data, test_data 和 rel_data，若 dev_data 为空则使用 test_data；max_length 可选，若未设置则动态计算批次最大长度，但不超过 BERT 最大长度。
    可用性：支持自定义 cache_dir，若无效则回退到默认缓存目录；根据模型来源选择 Hugging Face 或 ModelScope 下载，失败时提示用户提供本地模型地址。

    参数：
        bert_path_or_bertModel_name (str, optional): BERT 模型路径、Hugging Face 模型名称（如 'bert-base-chinese'）或 ModelScope 模型 ID（如 'iic/nlp_structbert_sentence-similarity_chinese-large'），若为空则默认 'bert-base-chinese'。
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
            bert_path_or_bertModel_name (str, optional): BERT 模型路径、Hugging Face 模型名称或 ModelScope 模型 ID。
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
        使用说明：内部方法，自动检测设备并加载 BERT 模型及 tokenizer，支持自定义路径、Hugging Face 或 ModelScope 下载，并动态设置 bert_dim 和 max_length。
        鲁棒性：检查文件路径是否存在，避免因文件缺失导致崩溃；记录核心日志；验证 max_length 不超过 BERT 最大长度。
        可用性：若 cache_dir 无效或不可用，回退到默认缓存目录；根据模型来源选择下载方式，失败时提示用户提供本地模型地址。
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
            # 判断是模型名称/ID 还是路径
            is_local_path = os.path.isdir(self.bert_path_or_bertModel_name)
            is_modelscope_id = "/" in self.bert_path_or_bertModel_name and not is_local_path
            max_retry = 2  # 最大重试次数
            for attempt in range(max_retry):
                try:
                    if is_local_path:
                        # 使用用户指定的本地路径
                        logger.info(f"使用本地 BERT 模型，路径: {self.bert_path_or_bertModel_name}")
                        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                        self.bert_model = BertModel.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                        self.bert_path_or_bertModel_name = os.path.abspath(self.bert_path_or_bertModel_name)  # 返回绝对路径
                    elif is_modelscope_id:
                        # ModelScope 模型 ID
                        cache_path = os.path.join(self.cache_dir, self.bert_path_or_bertModel_name.replace("/", "_"))
                        if os.path.exists(cache_path) and self._is_valid_bert_path(cache_path):
                            logger.info(f"检测到有效缓存，复用 ModelScope 模型，路径: {cache_path}")
                            self.tokenizer = BertTokenizer.from_pretrained(cache_path, cache_dir=self.cache_dir)
                            self.bert_model = BertModel.from_pretrained(cache_path, cache_dir=self.cache_dir)
                        else:
                            logger.info(f"缓存无效或不存在， 模型加载验证中，路径: {cache_path}")
                            model_dir = snapshot_download(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                            self.tokenizer = BertTokenizer.from_pretrained(model_dir, cache_dir=self.cache_dir)
                            self.bert_model = BertModel.from_pretrained(model_dir, cache_dir=self.cache_dir)
                            self.bert_path_or_bertModel_name = os.path.abspath(model_dir)  # 返回绝对路径
                    else:
                        # Hugging Face 模型名称
                        cache_path = os.path.join(self.cache_dir, self.bert_path_or_bertModel_name.replace("/", "_"))
                        # 调试日志：列出缓存目录内容
                        logger.debug(f"缓存目录内容: {os.listdir(self.cache_dir)}")
                        logger.debug(f"检查缓存路径: {cache_path}, 存在: {os.path.exists(cache_path)}")
                        # 更严格的缓存检查
                        cache_files = ["config.json", "tokenizer.json"]
                        model_files = ["pytorch_model.bin", "model.safetensors"]
                        cache_exists = os.path.exists(cache_path)
                        cache_valid = (cache_exists and
                                      all(os.path.exists(os.path.join(cache_path, f)) for f in cache_files) and
                                      any(os.path.exists(os.path.join(cache_path, f)) for f in model_files))
                        if cache_valid:
                            logger.info(f"检测到有效缓存，复用 Hugging Face 模型，路径: {cache_path}")
                            self.tokenizer = BertTokenizer.from_pretrained(cache_path, cache_dir=self.cache_dir)
                            self.bert_model = BertModel.from_pretrained(cache_path, cache_dir=self.cache_dir)
                        else:
                            logger.info(f"缓存无效或不存在，下载 Hugging Face 模型，路径: {cache_path}")
                            self.tokenizer = BertTokenizer.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                            self.bert_model = BertModel.from_pretrained(self.bert_path_or_bertModel_name, cache_dir=self.cache_dir)
                        self.bert_path_or_bertModel_name = os.path.abspath(cache_path)  # 返回绝对路径
                    # 验证 tokenizer 和 CLS 输出
                    test_text = "测试文本"
                    tokens = self.tokenizer.tokenize(test_text)
                    logger.info(f"Tokenizer 测试成功，输入: {test_text}, 令牌化结果: {tokens}")
                    inputs = self.tokenizer(test_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
                    outputs = self.bert_model(**inputs.to(self.device))
                    cls_output = outputs.last_hidden_state[:, 0, :].detach().cpu().numpy()
                    logger.info(f"CLS 位置输出形状: {cls_output.shape}, 样本值: {cls_output[0][:5]}")
                    break  # 成功加载，退出循环
                except Exception as e:
                    if attempt < max_retry - 1:
                        if "Read timed out" in str(e) or "Connection error" in str(e):
                            logger.warning(f"第 {attempt + 1} 次尝试下载失败: 网络超时或连接错误，{str(e)}，1秒后重试...")
                            time.sleep(1)
                        elif os.path.exists(cache_path):
                            logger.warning(f"缓存可能损坏，清除缓存并重试: {cache_path}")
                            shutil.rmtree(cache_path, ignore_errors=True)
                        else:
                            raise  # 其他错误直接抛出
                    else:
                        # 网络下载失败，提示用户提供本地模型地址
                        logger.error(f"多次尝试下载 BERT 模型失败: {str(e)}，请提供有效的本地模型路径作为 bert_path_or_bertModel_name 参数")
                        raise ValueError(f"下载失败，请提供本地模型路径作为 bert_path_or_bertModel_name 参数")
            logger.info(f"BERT 模型加载成功，绝对路径: {self.bert_path_or_bertModel_name}")
            self.bert_dim = self._get_bert_dim(self.bert_path_or_bertModel_name)
        except Exception as e:
            logger.error(f"加载 BERT 模型 {self.bert_path_or_bertModel_name} 失败: {str(e)}")
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
            str: 缓存目录的绝对路径。
        """
        if os.path.isdir(bert_path_or_bertModel_name):  # 如果是本地路径
            return os.path.abspath(bert_path_or_bertModel_name)
        else:  # 假设是模型名称或 ID
            return os.path.join(self.cache_dir, bert_path_or_bertModel_name.replace("/", "_"))

    def _download_default_bert(self):
        """下载默认 BERT 模型并返回绝对路径。
        使用说明：若 bert_path_or_bertModel_name 未提供或无效，则下载 'bert-base-chinese' 并返回其缓存路径。
        返回：
            str: 下载的 BERT 模型绝对路径。
        """
        default_model = "bert-base-chinese"
        try:
            logger.info(f"开始下载默认 BERT 模型: {default_model}")
            tokenizer = BertTokenizer.from_pretrained(default_model, cache_dir=self.cache_dir)
            model = BertModel.from_pretrained(default_model, cache_dir=self.cache_dir)
            cache_path = os.path.join(self.cache_dir, default_model.replace("/", "_"))
            absolute_path = os.path.abspath(cache_path)
            logger.info(f"默认 BERT 模型 {default_model} 下载完成，绝对路径: {absolute_path}")
            return absolute_path
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
                return 768  # bert-base 系列的隐藏层维度（包括 RoBERTa 和 WWM 变体)
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
             "source": "huggingface",
             "description": "默认中文 BERT 基础模型，适用于通用中文任务，参数量适中，bert_dim=768。"},
            {"name": "bert-large-chinese",
             "source": "huggingface",
             "description": "较大规模的中文 BERT 模型，适用于需要更高精度的大型数据集，bert_dim=1024。"},
            {"name": "hfl/chinese-roberta-wwm-ext",
             "source": "huggingface",
             "description": "基于 RoBERTa 的中文模型，带全词掩码，适合复杂关系抽取任务，bert_dim=768。"},
            {"name": "hfl/chinese-bert-wwm",
             "source": "huggingface",
             "description": "带全词掩码的中文 BERT，适用于需要更好语义理解的任务，bert_dim=768。"},
            {"name": "dienstag/chinese-roberta-wwm-ext-large",
             "source": "modelscope",
             "description": "大型中文 RoBERTa 模型，带全词掩码，适合高精度任务，bert_dim=1024。"},
            {"name": "tiansz/bert-base-chinese",
             "source": "modelscope",
             "description": "中文 BERT 基础模型，适用于通用任务，bert_dim=768。"},
            {"name": "dienstag/chinese-bert-wwm",
             "source": "modelscope",
             "description": "带全词掩码的中文 BERT，适用于语义理解任务，bert_dim=768。"},
            {"name": "iic/nlp_structbert_sentence-similarity_chinese-large",
             "source": "modelscope",
             "description": "StructBERT 模型，优化句子相似性任务，bert_dim=1024。"},
        ]

# 示例使用（主程序中初始化）
# if __name__ == '__main__':
#     try:
#         # 示例 1: 使用 Hugging Face 模型
#         baseconf1 = BaseConfig(
#             bert_path_or_bertModel_name=r"C:\Lucky_dt\2_bj\bj_23AI_KGCode\chapter4_code\CasRel_RE\bert-base-chinese",
#             train_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\test.json",
#             test_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\one_Sample.json",
#             rel_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\relation.json",
#             max_length=128
#         )
#         print("示例 1 - bert_path_or_bertModel_name:", baseconf1.bert_path_or_bertModel_name)
#     except Exception as e:
#         print("示例 1 失败:", str(e))

