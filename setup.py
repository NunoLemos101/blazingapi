from setuptools import setup, find_packages

setup(
    name='blazingapi',
    author='Nuno Lemos',
    author_email='nunolemos6zw5@gmail.com',
    description='A growing framework for building web applications.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version='0.0.41',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'bcrypt',
        'click',
        'gunicorn',
    ],
    entry_points={
        'console_scripts': [
            'blazingapi-admin=blazingapi.admin:blazingapi_admin',
        ],
    },
)
