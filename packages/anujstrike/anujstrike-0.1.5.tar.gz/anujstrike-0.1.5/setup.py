from setuptools import setup, find_packages

setup(
    name="anujstrike",
    version="0.1.5",  # Increment version every update
    author="Anuj Prajapati",
    description="AnujStrike - Offensive Toolkit with GUI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/anujstrike/",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "scapy",
        "psutil"
    ],
    entry_points={
        "console_scripts": [
            "anujstrike=anujstrike.main:main",
            "anujstrike-gui=anujstrike.gui_anujstrike:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
