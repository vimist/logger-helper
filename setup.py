"""Logger Helper.

A simple way to gather verbose logs from your application.
"""

from setuptools import setup


setup(
    name='logger-helper',
    version='0.0.5',
    author='Vimist',
    description='A simple way to gather verbose logs from your application!',
    long_description=open('README.rst').read(),
    url='https://github.com/vimist/logger-helper',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring'
    ],
    py_modules=['logger_helper']
)
