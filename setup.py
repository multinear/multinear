from setuptools import setup, find_packages

setup(
    name='multinear',
    version='0.1.5',
    packages=find_packages(exclude=['*.frontend*', '*.templates*']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'multinear=multinear.cli.main:main',
        ],
    },
    install_requires=[
        'autoevals>=0.0.105',
        'fastapi[standard]>=0.103',
        'jinja2>=3.1.4',
        'openai>=1.55.0',
        'rich>=13.9.4',
        'sqlalchemy>=2.0.36',
        'tqdm>=4.67.0',
        'uvicorn[standard]>=0.23',
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
            'frontend/build/**/*',
            'templates/*',
        ],
    },
    exclude_package_data={
        'multinear': [
            'frontend/.svelte-kit/**/*',
            'frontend/**/.svelte-kit/**/*',
        ],
    },
)
