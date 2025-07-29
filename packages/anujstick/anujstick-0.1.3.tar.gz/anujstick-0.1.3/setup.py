from setuptools import setup, find_packages

setup(
    name='anujstick',
    version='0.1.3',
    description='AnujStrike - Offensive Strike Toolkit with Advanced GUI',
    author='Anuj Prajapati',
    author_email='your_email@example.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'anujstick=anujstick.main:main',
            'anujstick-gui=anujstick.gui_app:launch_gui',
            'anujstrike=anujstick.advanced_gui:main'
        ]
    },
    python_requires='>=3.6',
)
