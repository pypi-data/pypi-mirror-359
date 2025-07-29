from setuptools import setup, find_packages

setup(
    name='dataupdater',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['flask'],
    author='Your Name',
    description='Live Python variable monitor and editor via web browser.',
    license='MIT',
)