# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

import sys, re
import setuptools
import pybind11

__version__ = "0.0.1"

ext_modules = [
    Pybind11Extension(
        "oilspillsim",
        ["src/utils/pywrap/pywrap.cpp",
         "src/utils/basic_simulator/basic_simulator.cpp",
         "src/utils/map/map.cpp",],
         include_dirs=[
            pybind11.get_include(False),
            pybind11.get_include(True ),
            "src/utils/basic_simulator",
            "src/utils/map",
            "src/Eigen",
        ],
        language='c++',
        # Example: passing in the version to the compiled code
        define_macros=[("VERSION_INFO", __version__)],
    ),
]

setup(
    name="oilspillsim",
    version=__version__,
    author="Alejandro Casado Pérez",
    author_email="acasado4@us.es",
    url="https://github.com/AloePacci/cpp_oil_simulator",
    description="First package version of Oil Spill simulator",
    long_description="",
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
