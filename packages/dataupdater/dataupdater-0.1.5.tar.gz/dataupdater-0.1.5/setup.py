from setuptools import setup, find_packages

setup(
    name='dataupdater',
    version='0.1.5',
    packages=find_packages(),               # <-- ✅ includes your source folder
    include_package_data=True,
    install_requires=['flask'],
    author='Anson Wong',
    description='A live Python variable editor via web interface',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)