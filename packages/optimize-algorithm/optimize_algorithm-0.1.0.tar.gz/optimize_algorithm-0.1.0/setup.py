from setuptools import setup, find_packages

setup(
    name='optimize_algorithm',
    version='0.1.0',
    description='collection of optimization algorithms, PSO & ABC',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Muhamad Dimas Wijaya',
    license='MIT License',
    url='https://github.com/MUHAMAD30DIMAS/optimize_algorithm.git',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib'
    ],
    python_requires='>=3.7'
)