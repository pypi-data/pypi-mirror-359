from transformers import AutoTokenizer
import os
import pkg_resources

class TokenCounter:
    def __init__(self):
        """
        初始化TokenCounter
        """
        try:
            # 获取tokenizer文件所在的目录
            tokenizer_path = pkg_resources.resource_filename('qwen_token_counter', 'tokenizer_files')
            
            # 确保所有必需的文件都存在
            required_files = ['tokenizer.json', 'vocab.json', 'merges.txt', 'tokenizer_config.json']
            for file in required_files:
                file_path = os.path.join(tokenizer_path, file)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"找不到必需的tokenizer文件: {file}")
            
            # 使用trust_remote_code=True来加载本地tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                tokenizer_path,
                local_files_only=True,
                trust_remote_code=True
            )
        except Exception as e:
            raise RuntimeError(f"初始化TokenCounter时出错: {str(e)}")
    
    def count_tokens(self, text):
        """
        计算文本的token数量
        Args:
            text: 输入文本
        Returns:
            int: token数量
        """
        return len(self.tokenizer.encode(text))

def get_token_count(text):
    """
    快速计算文本的token数量的便捷函数
    Args:
        text: 输入文本
    Returns:
        int: token数量
    """
    counter = TokenCounter()
    return counter.count_tokens(text)

__version__ = '0.1.0' 