from setuptools import setup, find_packages
setup(
    name="simplygame",
    version='1.0',
    author='CEDZEE', 
    author_email='cedzee.contact@gmail.com',
    url='https://github.com/cedzeedev/simplygame',
    description='A package to create games more easily',
    packages=find_packages(),
    readme='README.md',
    install_requires='pygame',
    python_requires=">=3.10",
    
)