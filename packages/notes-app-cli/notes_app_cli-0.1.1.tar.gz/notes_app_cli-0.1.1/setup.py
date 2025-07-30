from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="notes-app-cli",
    version="0.1.1",
    description="A CLI tool for adding and reviewing notes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tejaaswini",
    py_modules=["main", "db", "utils", "notes_semantic_db"],
    install_requires=[
        "rich>=10.0.0",
        "questionary>=2.0.0",
        "chromadb",
        "sentence-transformers"
    ],
    entry_points={
        "console_scripts": [
            "notes=main:main",
        ],
    },
    python_requires=">=3.7",
) 