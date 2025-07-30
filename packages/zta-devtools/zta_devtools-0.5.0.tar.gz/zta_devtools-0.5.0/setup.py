from setuptools import setup, find_packages

setup(
    name="zta-devtools",
    version="0.3.0",
    description="A Python CLI tool for developers with package management and vulnerability scanning.",
    author="ZtaMDev",
    author_email="manuelitoricardo20092023@gmail.com",
    url="https://github.com/ZtaMDev/zta-devtools",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "rich",
        "watchdog",
        "safety"
    ],
    entry_points={
        "console_scripts": [
            "devtools_cli=devtools_cli.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    include_package_data=True,
)
