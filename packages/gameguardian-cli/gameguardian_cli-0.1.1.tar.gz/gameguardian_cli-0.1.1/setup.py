from setuptools import setup, find_packages

setup(
    name='gameguardian-cli',
    version='0.1.1',
    author='Dx4Grey',
    description='Python CLI version of Game Guardian',
    packages=find_packages(),
    install_requires=[],  # Tambahin kalau ada dependensi kayak "psutil", dll
    entry_points={
        'console_scripts': [
            'ggcli = gameguardian_cli.__main__:main',
        ],
    },
    python_requires='>=3.6',
)
