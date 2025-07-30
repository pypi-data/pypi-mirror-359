from setuptools import setup, find_packages

setup(
    name='diff-check-cli',
    version='0.1.0',
    description='CLI для сравнения файлов/директорий/git-объектов',
    author='Daniil Astrouski',
    author_email='shelovesuastra@gmail.com',
    packages=find_packages(),
    install_requires=[
        'click',
        'rich',
        'prompt-toolkit',
    ],
    entry_points={
        'console_scripts': [
            'diff-check=diff_check_cli.cli:main',
        ],
    },
    python_requires='>=3.7',
) 