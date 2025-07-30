from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='diff-check-cli',
    version='0.1.4',
    description='CLI для сравнения файлов/директорий/git-объектов',
    long_description=long_description,
    long_description_content_type="text/markdown",
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