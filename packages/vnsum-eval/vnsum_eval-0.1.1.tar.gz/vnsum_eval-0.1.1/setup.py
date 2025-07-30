from setuptools import setup, find_packages

setup(
    name="vnsum_eval",  
    version="0.1.1",     
    packages=find_packages(),
    install_requires=[
        "bert-score>=0.3.13",
        "torch>=1.7.0",
        "transformers>=4.0.0"
    ],
    author="Khang Nguyễn",
    author_email="vipboy20031408@gmail.com",
    description="Thư viện đánh giá tóm tắt tiếng Việt bằng BERTScore",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
