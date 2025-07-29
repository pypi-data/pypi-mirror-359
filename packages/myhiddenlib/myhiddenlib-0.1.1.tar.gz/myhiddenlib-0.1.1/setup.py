from setuptools import setup, find_packages

setup(
    name="myhiddenlib",                      # название для pip
    version="0.1.1",
    description="My Hidden Utility Library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vitya",
    author_email="vitya@example.com",
    url="https://github.com/yourname/myhiddenlib",  # опционально
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)