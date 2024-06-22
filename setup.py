import os
from glob import glob

import toml
from setuptools import Extension, setup

with open("./README.md") as f:
    long_desc: str = f.read()

if __name__ == "__main__":
    with open("./pyproject.toml", "r") as f:
        data = toml.load(f)
    setup(
        name="view.py",
        version="1.0.0-alpha11",
        packages=["view"],
        project_urls=data["project"]["urls"],
        package_dir={"": "src"},
        license="MIT",
        ext_modules=[
            Extension(
                "_view",
                glob("./src/_view/*.c"),
                extra_compile_flags=['-g3']
            )
        ],
        include_dirs=["./include"],
    )
