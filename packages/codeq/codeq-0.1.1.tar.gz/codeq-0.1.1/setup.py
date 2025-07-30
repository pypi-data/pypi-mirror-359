from setuptools import setup, find_packages

setup(
    name='codeq',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'click', 'radon', 'rich'
    ],
    entry_points={
        'console_scripts': [
            'codeq=codeq.cli:analyze',
        ],
    },
    author='Ashwin Joshi',
    description='CLI tool for Python code quality metrics and smell detection',
    python_requires='>=3.7',
)
