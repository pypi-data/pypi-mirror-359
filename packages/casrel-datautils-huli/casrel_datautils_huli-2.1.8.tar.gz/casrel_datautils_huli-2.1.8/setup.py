from setuptools import setup, find_packages

setup(
    name="casrel_datautils_huli",
    version="2.1.8",
    packages=find_packages(),
    license="MIT", #指定许可证类型
    license_files=("LICENSE"), #制定许可证文件
    install_requires=[
        "torch",
        "transformers>=4.0.0",  # 指定最低版本为 4.0.0
    ],
    author="lily",
    description="A Chinese relation extraction data utility toolkit based on CasRel model",
    long_description=open("README.md", encoding='utf-8').read(),  # 显式指定 UTF-8 编码,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/casrel_datautils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)