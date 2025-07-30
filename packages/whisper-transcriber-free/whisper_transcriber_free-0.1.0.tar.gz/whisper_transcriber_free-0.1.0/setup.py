from setuptools import setup, find_packages

setup(
    name="whisper-transcriber-free",
    version="0.1.0",
    description="A Python SDK for audio transcription using Whisper",
    author="raedrdhaounia",
    author_email="raedrdhaounia@gmail.com",
    url="https://github.com/raedrdhaounia/whisper-transcriber",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "openai-whisper @ git+https://github.com/openai/whisper.git@main",
        "pydantic>=2.4.2",
        "python-multipart>=0.0.6",
        "aiohttp>=3.9.1",
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
