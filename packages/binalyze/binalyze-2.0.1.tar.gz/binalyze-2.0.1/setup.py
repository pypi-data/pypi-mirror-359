from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="binalyze",
    version="2.0.1",
    author="Binalyze",
    author_email="support@binalyze.com",
    description="Complete Python SDK for Binalyze Products - AIR, Fleet, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/binalyze/python-sdk",
    packages=find_packages(exclude=["tests_*", "tests_*.*", "tools", "tools.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.1",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "python-dateutil>=2.8.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "isort",
            "mypy",
            "flake8",
            "pylint",
        ],
        "testing": [
            "pytest>=6.0",
            "pytest-cov",
            "pytest-mock",
        ],
        "env": [
            "python-dotenv>=0.19.0",
        ],
        "full": [
            "python-dotenv>=0.19.0",
            "pytest>=6.0",
            "pytest-cov",
            "pytest-mock",
            "black",
            "isort",
            "mypy",
            "flake8",
            "pylint",
        ],
    },
    keywords="binalyze air fleet forensics security api sdk digital-forensics incident-response dfir",
    project_urls={
        "Bug Reports": "https://github.com/binalyze/python-sdk/issues",
        "Source": "https://github.com/binalyze/python-sdk",
        "Documentation": "https://github.com/binalyze/python-sdk/blob/main/README.md",
        "Binalyze": "https://binalyze.com",
        "AIR Product": "https://binalyze.com/products/air/",
    },
    entry_points={
        "console_scripts": [
            "binalyze-air=binalyze.air.cli:main",
        ],
    },
)
