# Qwen Token Counter

一个简单的Qwen模型系列token计数工具。

## 安装

```bash
pip install qwen-token-counter
```

## 使用方法

有两种使用方式：

1. 快速单次使用：

```python
from qwen_token_counter import get_token_count

text = "你好，世界！"
count = get_token_count(text)
print(f"Token数量: {count}")
```

2. 多次使用（推荐）：

```python
from qwen_token_counter import TokenCounter

counter = TokenCounter()
text1 = "你好，世界！"
text2 = "Hello, World!"

count1 = counter.count_tokens(text1)
count2 = counter.count_tokens(text2)

print(f"文本1的Token数量: {count1}")
print(f"文本2的Token数量: {count2}")
```

## 特点

- 轻量级：只包含必要的tokenizer文件
- 易用：简单的API设计
- 高效：支持批量文本处理
- 准确：使用官方Qwen tokenizer

## 依赖

- Python >= 3.7
- transformers >= 4.51.0

## License

MIT License 