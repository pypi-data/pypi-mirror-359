from setuptools import setup, find_packages

setup(
    name='anujstick',
    version='0.1.1',
    description='AnujStrike - Offensive Strike Toolkit by Anuj Prajapati',
    author='Anuj Prajapati',
    author_email='your_email@example.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'anujstick=anujstick.main:main'
        ]
    },
    python_requires='>=3.6',
)
