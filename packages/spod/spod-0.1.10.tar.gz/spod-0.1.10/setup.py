from setuptools import find_packages, setup

setup(
    name="spod",
    version="0.1.10",
    py_modules=["spod"],
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "spod = spod.spod:cli",
        ],
    },
    packages=find_packages(),
    package_data={"spod": ["templates/*.sh"]},
    include_package_data=True,
)
