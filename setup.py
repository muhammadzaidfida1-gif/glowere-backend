from setuptools import setup, find_packages

setup(
    name="glowere-backend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "Pillow",
        "torch",
        "torchvision",
        "httpx",
        "python-dotenv",
    ],
)
