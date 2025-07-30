import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chatip",
    version="0.1",
    author="Wu_Ziqi",
    author_email="bcm_copilot@outlook.com",
    description="一个简单的 IP 处理工具（示例）",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        'Pillow>=5.1.0',
        'numpy==1.26.4',  # 注意：numpy 1.26.4 可能不完全兼容 3.13
    ],
    entry_points={
        'console_scripts': [
            'chatip=chatip.converter:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",  # 明确支持 3.13
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9, <3.14',  # 修正：使用<3.14表示小于3.14的所有版本
)
