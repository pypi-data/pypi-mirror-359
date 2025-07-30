from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hitesh-fastapi-starter",
    version="1.1.7",
    author="Hitesh Ladumor",
    author_email="thingswhat88@gmail.com",
    description="Generate a FastAPI starter project structure. This version solve many bugs and security ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hitesh26682/hitesh-fastapi-starter",
    packages=find_packages(),
    install_requires=[
        "fastapi",
    ],
    entry_points={
        "console_scripts": [
            "hitesh-fastapi-starter=fastapi_starter.generator:create_project_cli"
        ],
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
