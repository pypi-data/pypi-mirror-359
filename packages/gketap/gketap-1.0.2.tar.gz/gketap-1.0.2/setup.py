
from setuptools import setup, find_packages

setup(
    name="gketap",
    version="1.0.2",
    description="A CLI tool to tap into GKE clusters via SSH tunnels",
    author="Cosmin Drula",
    url="https://github.com/drulacosmin/gketap",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml",
        "psutil",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "gketap=gketap.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
