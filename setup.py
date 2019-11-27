from setuptools import setup

setup(
    name='reqtime',
    version='0.1.1',
    py_modules=['reqtime'],
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'tabulate'
    ],
    entry_points='''
        [console_scripts]
        reqtime=reqtime:cli
    ''',
)