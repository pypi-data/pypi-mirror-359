from setuptools import setup, find_packages

setup(
    name="anujstrike",
    version="0.1.4",  # <-- Bump this for each upload
    description="AnujStrike Offensive Toolkit with GUI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Anuj Prajapati",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "scapy",
        "requests",
        "psutil"
    ],
    entry_points={
        'console_scripts': [
            'anujstrike = anujstrike.main:main',
            'anujstrike-gui = anujstrike.gui:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
