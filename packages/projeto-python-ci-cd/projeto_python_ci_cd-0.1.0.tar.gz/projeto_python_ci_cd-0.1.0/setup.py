from setuptools import setup, find_packages

setup(
    name='projeto-python-ci-cd',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='Projeto exemplo com CI/CD usando GitHub Actions',
    author='Mencarini',
    author_email='ericmencarini@outlook.com',
    url='https://github.com/EricMencarini/projeto-python-ci-cd',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
