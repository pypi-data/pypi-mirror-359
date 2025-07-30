from setuptools import setup, find_packages

setup(
    name='carsxe-api',
    version='0.1.1',
    author='Omar Walied',
    author_email='omar.walied@carsxe.com',
    description='CarsXE API PIP Package',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests',
        'urllib3',
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
