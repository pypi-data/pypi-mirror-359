# setup.py

from setuptools import setup, find_packages

setup(
    name='pysomit',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
    ],
    description='SOMIT library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Dr. Zhiyuan Wang',
    author_email='wang1399@e.ntu.edu.sg',
    url='https://github.com/Dr-WangZhiyuan/pysomit',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
