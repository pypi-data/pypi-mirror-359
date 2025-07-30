from setuptools import setup, find_packages

setup(
    name="test_auto_publish_lib_unique2",
    version="0.1.0",
    packages=find_packages(),
    author="HEAVEN Agent",
    author_email="heaven.demo.agent@gmail.com",
    description="A unique test package for agent-native PyPI auto-publishing.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/heaven-agent/unique-test2",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
