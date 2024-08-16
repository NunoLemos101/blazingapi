from setuptools import setup, find_packages

setup(
    name='blazingapi',
    author='Nuno Lemos',
    author_email='nunolemos6zw5@gmail.com',
    description='A growing framework for building web applications.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version='0.0.43',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'bcrypt',
        'click',
        'gunicorn',
        'jsonschema>=3.2.0',
        'psycopg2',
        'psycopg2-binary',
        'mysql-connector-python'
    ],
    entry_points={
        'console_scripts': [
            'blazingapi-admin=blazingapi.admin:blazingapi_admin',
        ],
    },
)
