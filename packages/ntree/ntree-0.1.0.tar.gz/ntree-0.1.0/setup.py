from setuptools import setup, find_packages

setup(
    name="ntree",
    version="0.1.0",
    description="A better version of the Linux tree command in Python",
    author="Vijay Satheesh",
    packages=find_packages(),
    install_requires=[
        "humanize"
    ],
    entry_points={
        "console_scripts": [
            "ntree=ntree.libntree:main"
        ]
    },
    python_requires=">=3.6",
)