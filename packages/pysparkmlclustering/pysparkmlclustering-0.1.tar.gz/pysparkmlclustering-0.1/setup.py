from setuptools import setup, find_packages

setup(
    name="pysparkmlclustering",  
    version="0.1",
    packages=find_packages(),
    install_requires=['pyperclip'],  
    author="Nick Fury",
    author_email="nmercado506@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)