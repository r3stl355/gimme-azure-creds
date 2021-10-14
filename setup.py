from setuptools import find_packages, setup

setup(
    name='gimme-azure-creds',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        "adal", 
        "databricks-cli"
    ],
    entry_points={
        'console_scripts': [
            'gimme-azure-creds=src.gimmeazurecreds:get_token',
        ],
    },
)
