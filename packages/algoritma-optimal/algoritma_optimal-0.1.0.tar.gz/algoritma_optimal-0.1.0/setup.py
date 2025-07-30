from setuptools import setup, find_packages

setup(
    name='algoritma_optimal',
    version='0.1.0',
    description='Kumpulan algoritma optimasi',
    author='Muhamad Dimas Wijaya',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib'
    ],
    python_requires='>=3.7'
)