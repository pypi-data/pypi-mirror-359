from setuptools import setup, find_packages

setup(
    name='heaven_test_package_herc01',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[],
    author='Isaac Rubin, Herc (HEAVEN agent)',
    author_email='isaacwrubin@gmail.com',
    description='This test package library was packaged by the HEAVEN agent Herc using the code packager for test purposes. We are in the process of building an automated microservice packaging system.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/heaven_test_package_herc01/',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
