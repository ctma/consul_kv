from setuptools import setup

setup(
    name='python2_consul',
    packages=['python2_consul'],
    version='0.0.1',
    install_requires=[
        'certifi==2017.7.27.1',
        'chardet==3.0.4',
        'idna==2.6',
        'PyYAML==5.4',
        'requests==2.18.4',
        'urllib3==1.22',
        'validators==0.12.0',
        'pytest==3.2.2'
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest',
        'mock'
    ]
)
