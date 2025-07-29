from setuptools import setup, find_packages
from gameguardian_cli.version import __version__

setup(
    name='gameguardian-cli',
    version=f'{__version__}',
    author='Dx4Grey',
    description='Python CLI version of Game Guardian',
    packages=find_packages(),
    install_requires=[],  # Tambahin kalau ada dependensi kayak "psutil", dll
    entry_points={
        'console_scripts': [
            'ggcli = gameguardian_cli.__main__:main',
        ],
    },
    python_requires='>=3.6'
)
