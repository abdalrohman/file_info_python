from setuptools import setup, find_packages

# or read from a requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='file_info',
    version='1.0',
    description='A Python script that can display some information about files and directories',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Abdulrahman Alnaseer',
    author_email='abdd199719@gmail.com',
    url='https://github.com/abdalrohman/file_info_python',
    license='GNU V3.0',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
