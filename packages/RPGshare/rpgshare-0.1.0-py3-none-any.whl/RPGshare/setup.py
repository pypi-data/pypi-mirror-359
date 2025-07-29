from setuptools import setup, find_packages

setup(
    name='RPGshare',
    version='0.1.0',
    description='中信证券榜单数据获取与处理库',
    author='tedelon',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6',
    license='MIT',
    url='',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
) 