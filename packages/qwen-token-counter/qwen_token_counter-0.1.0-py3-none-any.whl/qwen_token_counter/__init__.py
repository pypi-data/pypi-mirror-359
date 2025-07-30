from transformers import AutoTokenizer
import os
import pkg_resources

class TokenCounter:
    def __init__(self):
        """
        初始化TokenCounter
        """
        tokenizer_path = pkg_resources.resource_filename('qwen_token_counter', 'tokenizer_files')
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    
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