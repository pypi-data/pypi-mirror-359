from setuptools import setup, find_packages

setup(
    name='anujstick',               # Your package name on PyPI
    version='0.1.0',                # Start with 0.1.0
    description='AnujStick - Your custom cybersecurity toolkit',
    author='Anuj Prajapati',
    author_email='your_email@example.com',
    url='https://github.com/yourusername/anujstick',  # Optional
    packages=find_packages(),
    install_requires=[],  # List dependencies if any
    entry_points={
        'console_scripts': [
            'anujstick=anujstick.main:main'  # CLI command (Optional)
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
