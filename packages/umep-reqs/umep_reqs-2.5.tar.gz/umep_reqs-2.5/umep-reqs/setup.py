from setuptools import setup, find_packages
from pathlib import Path

with open(Path(__file__).parent.parent / "README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="umep-reqs",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(),
    install_requires=[
        "supy==2025.6.2.dev0",
        "numba==0.59.0",
        "jaydebeapi==1.2.3",
        "netCDF4",
        "openpyxl",
        "rioxarray",
        "pydantic",
        "target-py",
    ],
    author="UMEP dev team",
    long_description=long_description,
    long_description_content_type="text/markdown",
)








# from setuptools import setup, find_packages
# from pathlib import Path

# import os


# def get_version():
    # try:
        # from setuptools_scm import get_version

        # if os.environ.get("GITHUB_ACTIONS") == "true":
            # # Use 'no-local-version' scheme for GitHub Actions
            # return get_version(local_scheme="no-local-version")
        # else:
            # # Use the default scheme for local environments
            # return get_version()
    # except ImportError:
        # print("setuptools_scm not installed, using default version '0.0'")
        # return "0.0"


# with open(Path(__file__).parent.parent / "README.md", "r", encoding="utf-8") as f:
    # long_description = f.read()

# setup(
    # name="umep-reqs",
    # version=get_version(),  # Use setuptools_scm to get version from git tags.
    # packages=find_packages(),
    # install_requires=[
        # "supy==2025.6.2.dev0",  # Replace with actual dependency and version number.
        # "numba==0.59.0",
        # "jaydebeapi==1.2.3",
        # "netCDF4",
        # "openpyxl",
        # "rioxarray",
        # "pydantic",
        # "target-py",        #   "dependency2==y.y.y" 
    # ],
    # author="UMEP dev team",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    
# )


