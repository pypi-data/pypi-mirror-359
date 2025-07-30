from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="streamlit-theta",
    version="1.0.2",
    author="CelsiaSolaraStarflare",
    author_email="celsiastarflare@outlook.com",
    description="Open source Streamlit Editor suite for documents, presentations, spreadsheets, and custom modules. Enhance your Streamlit apps with visual editing tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arcana/streamlit-theta",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Multimedia :: Graphics :: Presentation",
    ],
    python_requires=">=3.7",
    install_requires=[
        "streamlit>=1.0.0",
    ],
    keywords="streamlit, editor, word, spreadsheet, presentation, visual, modules, custom, open source",
    project_urls={
        "Bug Reports": "https://github.com/arcana/streamlit-theta/issues",
        "Source": "https://github.com/arcana/streamlit-theta",
    },
)