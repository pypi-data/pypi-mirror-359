from setuptools import setup, find_packages

setup(
    name="aromatools",
    version="0.1.0",
    packages=find_packages(where="aromatools"),
    package_dir={"": "aromatools"},
    description="Herramientas para el análisis de aromaticidad",
    author="Fernando Martínez Villarino",
    author_email="fernandomv5897@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "arogeometric = aromatools.arogeometric.__main__:main"
        ]
    },
    python_requires=">=3.12",
    install_requires=[
        "numpy",
        "networkx",
        "matplotlib",
        "art",
        "ase"
    ],
)
