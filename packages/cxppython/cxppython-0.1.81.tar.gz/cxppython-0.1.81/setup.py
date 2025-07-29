from setuptools import setup, find_packages

setup(
    name="cxppython",              # 包名
    version="0.1.81",                # 版本号
    packages=find_packages(exclude=["tests", "tests.*"]),       # 自动找到所有包
    description="A python utils package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="cxp",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/my_package",  # 项目主页（可选）
    license="MIT",
    install_requires=[
        "pymysql>=1.1.0,<2.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "requests>=2.30.0,<3.0",
        "colorama~=0.4.6",
        "python-statemachine>=2.1,<3.0.0",
        "munch~=2.5.0",
        "pyyaml>=6.0,<7.0",
        "SQLAlchemy[asyncio]>=2.0.25,<3.0.0",
        "pydantic>=2.0.0,<3.0",
        "cryptography>=40.0,<45.0",
        "pymongo~=4.12.0",
        "redis~=6.2.0",
        "aiomysql~=0.2.0"

    ],  # 依赖（可选）
    classifiers=[                   # 元数据
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",        # 支持的 Python 版本
)