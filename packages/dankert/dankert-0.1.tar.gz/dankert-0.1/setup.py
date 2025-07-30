from setuptools import setup, find_packages

setup(
    name="dankert",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dankert=dankert.__main__:main',
        ],
    },
    author="DanKert",
    description="Легендарная CLI-команда от DanKert",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
)
