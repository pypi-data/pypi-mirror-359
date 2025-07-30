from setuptools import setup, find_packages

setup(
    name="test_auto_publish_lib",
    version="0.1.0",
    packages=find_packages(),
    author="HEAVEN Test",
    author_email="heaven.demo.agent@gmail.com",
    description="A test package for automated PyPI publishing via HEAVEN.",
    long_description="Testing our auto-publish tool.",
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/your-repo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
