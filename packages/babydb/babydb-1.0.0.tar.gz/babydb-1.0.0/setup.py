from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="babydb",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'simpledb-cli = simpledb.cli:run_cli',
            'simpledb-web = simpledb.web:run_web',
        ],
    },
    package_data={
        'simpledb': ['config.ini', 'index.html'],
    },
    author="Ashish Babu",
    author_email="ashuwarrior304@gmail.com",
    description="A lightweight key-value database with compression",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
