from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitsc",
    version="1.0.0",
    author="Pradyut Das",
    author_email="daspradyut516@gmail.com",
    description="AI-powered semantic git commit message generator using Groq's LLaMA models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prxdyut/gitsc",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.6",
    install_requires=["groq", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "gitsc=gitsc.cli:main",
        ],
    },
) 