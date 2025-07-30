from setuptools import setup, find_packages
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

# 获取tokenizer文件
extra_files = package_files('qwen_token_counter/tokenizer_files')

# 读取README.md，使用UTF-8编码
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qwen_token_counter",
    version="0.1.0",
    author="benoqtr",
    author_email="benoqtr@gmail.com",
    description="A simple token counter for Qwen model series",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/benoqtr/qwen_token_counter",
    packages=find_packages(),
    package_data={
        'qwen_token_counter': ['tokenizer_files/*'] + extra_files
    },
    install_requires=[
        'transformers>=4.51.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
) 