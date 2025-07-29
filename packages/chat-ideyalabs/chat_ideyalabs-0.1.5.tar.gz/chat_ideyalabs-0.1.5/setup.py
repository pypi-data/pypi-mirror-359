"""
Secure setup configuration for ChatIdeyalabs package.
This file contains NO sensitive information and is safe for PyPI distribution.
"""

from setuptools import setup, find_packages

# Read long description from sanitized file
try:
    with open("PYPI_PUBLISHING_GUIDE.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "ChatIdeyalabs - Secure LLM API wrapper with user authentication"

# Read requirements
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "motor>=3.3.0",
        "pymongo>=4.5.0",
        "python-multipart>=0.0.6",
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
    ]

setup(
    name="chat-ideyalabs",
    version="0.1.5",  # Update this for each release
    author="Ideyalabs",
    author_email="support@ideyalabs.com",
    description="Secure LLM API wrapper with user authentication and request validation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ideyalabs/chat-ideyalabs",
    project_urls={
        "Bug Tracker": "https://github.com/ideyalabs/chat-ideyalabs/issues",
        "Documentation": "https://github.com/ideyalabs/chat-ideyalabs/blob/main/PYPI_PUBLISHING_GUIDE.md",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "build": [
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chat-ideyalabs-server=chat_ideyalabs.api.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "chat_ideyalabs": [
            "*.md",
            "*.txt",
            "*.json",
        ],
    },
    keywords=[
        "llm",
        "chatbot",
        "api",
        "authentication",
        "security",
        "openai",
        "langchain",
        "artificial-intelligence",
        "machine-learning",
    ],
    zip_safe=False,  # Allow access to package files
) 