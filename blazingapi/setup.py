from setuptools import setup, find_packages

setup(
    name='framework',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'framework-admin=admin:framework_admin',
        ],
    },
)
