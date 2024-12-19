#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sentry_feishu_gsmini",
    version='1.5',
    author='gsmini',
    author_email='gsmini@sina.cn',
    url='https://github.com/gsmini/sentry-feishu',
    description='A Sentry extension which send errors stats to FeiShu',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='sentry feishu notify',
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'sentry.plugins': [
            'sentry_feishu_gsmini = sentry_feishu_gsmini.plugin:FeiShuPlugin'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
    ]
)
