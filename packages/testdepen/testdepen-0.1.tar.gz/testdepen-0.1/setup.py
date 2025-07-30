from setuptools import setup

setup(
    name='testdepen',
    version='0.1',
    dependency_links=[
        'https://github.com/mhammond/pywin32/archive/refs/tags/b306.tar.gz#egg=pywin32'
    ]
)