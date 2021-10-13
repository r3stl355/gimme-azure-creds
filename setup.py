from setuptools import setup

setup(
    name='gimme-azure-creds',
    version='0.1.0',
    py_modules=['gimmeazurecreds'],
    install_requires=[
        'Click',
        "adal", 
        "databricks-cli"
    ],
    entry_points={
        'console_scripts': [
            'gimme-azure-creds=gimmeazurecreds:get_token',
        ],
    },
)
