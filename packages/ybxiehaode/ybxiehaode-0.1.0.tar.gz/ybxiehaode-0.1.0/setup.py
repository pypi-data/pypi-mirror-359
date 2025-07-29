# -*- coding: utf-8 -*-
# @Author  : 鱼玄机
# @File    : setup.py
# @Time    : 2025/6/30 20:28
# setup.py
from setuptools import setup, find_packages

setup(
    name='ybxiehaode',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pygame>=2.0.0'
    ],
    entry_points={
        'console_scripts': [
            'ybxiehaode=ybxiehaode.main:main',
        ],
    },
    author='yb',
    author_email='xuanjiyv@163.com',
    description='一个炫酷的 AI 烟花秀动画，展示三生万物',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
