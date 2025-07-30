from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="spliit_client",
    version="0.1.0",
    description="A Python client for the Spliit API (group expense sharing)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Abhinav",
    author_email="gptabhinav0148@gmail.com",
    url="https://github.com/abg0148/spliit_client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "twine>=3.0",
            "build>=0.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "spliit=spliit_client.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="spliit, expense, sharing, api, client, group, expenses",
    project_urls={
        "Bug Reports": "https://github.com/abg0148/spliit_client/issues",
        "Source": "https://github.com/abg0148/spliit_client",
        "Documentation": "https://github.com/abg0148/spliit_client#readme",
    },
) 