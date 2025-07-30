from setuptools import setup

setup(
    name="hello-world-你的用户名",  # 请将"你的用户名"替换为您的PyPI用户名
    version="0.1.0",
    packages=["hello_world"],
    author="您的名字",
    author_email="您的邮箱",
    description="一个简单的Hello World包",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/你的用户名/项目名",  # 如果有GitHub仓库，请更新此URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 