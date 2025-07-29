from pathlib import Path
from setuptools import setup, find_packages

setup(
    name="financial-engine",
    version="0.1.0",
    author="Raj Adhikari",
    author_email="adhikarirajj07@gmail.com",
    description="Async financial-ratio engine using MongoDB + S3",
    long_description = Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/financial-engine",
    project_urls={
        "GitHub": "https://github.com/r-adhikari97",
        "LinkedIn": "https://www.linkedin.com/in/adhikari-raj/",
    },
    packages=find_packages(),
    install_requires=[
        "motor",
        "pydantic",
        "python-dotenv",
        "pandas",
        "aioboto3",
        "pyarrow",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    license="MIT",
)
