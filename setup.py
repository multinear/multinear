from setuptools import setup, find_packages

setup(
    name='multinear',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'multinear=multinear.cli.main:main',
        ],
    },
    install_requires=[
        # Any dependencies your package has
    ],
    author='Dima Kuchin',
    author_email='dima@mirable.io',
    description='Multinear platform',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/multinear/multinear',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    package_data={
        'multinear': [
            'frontend/*',
            'frontend/**/*',
            '!frontend/node_modules/**/*',  # Exclude node_modules
            '!frontend/.env',  # Exclude .env
        ],
    },
)
