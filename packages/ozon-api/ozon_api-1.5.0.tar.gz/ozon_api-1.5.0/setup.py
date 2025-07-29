from setuptools import find_packages, setup
from ozon_api import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ozon-api",
    version=__version__,
    author="Artem Navodniuk",
    author_email="dev@fxcode.ru",
    description="Асинхронная Python библиотека для работы с API Ozon Seller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mephistofox/python-ozon-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
    ],
    keywords=["ozon", "api", "seller", "marketplace", "async", "aiohttp"],
    project_urls={
        "Bug Tracker": "https://github.com/mephistofox/python-ozon-api/issues",
        "Documentation": "https://github.com/mephistofox/python-ozon-api#readme",
        "Source Code": "https://github.com/mephistofox/python-ozon-api",
    },
)
