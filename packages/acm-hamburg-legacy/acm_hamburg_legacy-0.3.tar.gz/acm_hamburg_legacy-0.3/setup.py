from setuptools import find_packages, setup

# some RDKit versions are not recognized by setuptools
# -> check if RDKit is installed by attempting to import it
# -> if RDKit can be imported, do not add it to install_requires
rdkit = False
try:
    from rdkit import Chem

    rdkit = True
except ImportError:
    pass

# rdkit 2022.3.3 is the oldest (reasonable) version
rdkit_requirement = ["rdkit>=2022.3.3"] if not rdkit else []

setup(
    name="acm-hamburg-legacy",
    version="0.3",
    maintainer="Johannes Kirchmair",
    maintainer_email="johannes.kirchmair@univie.ac.at",
    packages=find_packages(),
    url="https://github.com/molinfo-vienna/acm-hamburg-legacy",
    description="Legacy code of the former ACM group in Hamburg",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    package_data={"": ["*.smarts"]},
    install_requires=rdkit_requirement
    + [
        "adjustText>=0.7.3",
        "cairosvg>=2.5.2",
        "matplotlib>=3.5.2",
        "molvs>=0.1.1",
        "numpy>=1.19.2",
        "pandas>=1.2.1",
        "scikit_learn>=0.20.0",
        "xlsxwriter>=3.0.3",
        "nerdd-module>=0.1.0",
    ],
    extras_require={
        "dev": [
            "mypy",
            "black",
        ],
        "test": [
            "pytest",
            "pytest-watch",
        ],
    },
    entrypoints={
        "nerdd-module.plugins": [
            "_ = acm.setup_hook:_setup_hook",
        ]
    },
)
