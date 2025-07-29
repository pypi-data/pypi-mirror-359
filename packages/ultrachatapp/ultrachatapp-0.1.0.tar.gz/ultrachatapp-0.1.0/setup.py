# setup.py

from setuptools import setup, find_packages

setup(
    name="ultrachatapp",
    version="0.1.0",
    packages=find_packages(),  # Automatically includes 'features' etc.
    include_package_data=True,
    install_requires=[
    "fastapi",
    "uvicorn",
    "pydantic",
    "cryptography",
    "pymongo",
    "sqlalchemy",
    "boto3",
    "python-dotenv",
    "python-multipart",
    "rapidfuzz",
    "requests",
    "aiofiles",
    
],
    entry_points={
    "console_scripts": [
        "ultrachat=ultrachatapp.main:main"   # ✅ Sahi
    ],
 },

    author="Yuvraj Thakur",
    description="UltraXpert Chat App with FastAPI",
    keywords="chatbot fastapi docker mongo",
)
