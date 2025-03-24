from setuptools import setup, find_packages

setup(
    name="visibrain",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pymongo",
        "python-dotenv",
        "httpx",
        "fastapi-cache2",
    ],
    python_requires=">=3.8,<3.13",
) 