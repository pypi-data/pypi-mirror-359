from setuptools import setup, find_packages, Extension


with open("README.md") as readme:
    long_description = readme.read()

with open(file="./ftp_brute_force/VERSION", mode="r", encoding="utf-8") as version:
    __VERSION__ = version.read()

c_extension = Extension(
    name="ftp_brute_force.load_dict",
    sources=["ftp_brute_force/load_dict.c"],
    include_dirs=[r"/home/jackson/.conda/envs/python3.13/include/python3.13"],
)

setup(
    name="ftp_brute",
    version=__VERSION__,
    author="Jackson Ja",
    author_email="jackson2937703346@163.com",
    description="A FTP brute force tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jacksonjapy/ftp_brute_force",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ftp_brute_force": ["VERSION", "*.so", "*.pyd", "*.pyi"],
    },
    exclude_package_data={
        "ftp_brute_force": ["load_dict.c"],
    },
    ext_modules=[c_extension],
    python_requires='>=3.10',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'ftp-brute = ftp_brute_force.ftp_brute_force:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
)