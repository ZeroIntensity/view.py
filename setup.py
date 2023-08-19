from setuptools import setup, Extension
import toml
from glob import glob

with open("./README.md") as f:
    long_desc: str = f.read()

if __name__ == "__main__":
    with open("./pyproject.toml", "r") as f:
        data = toml.load(f)

    setup(
        name="view.py",
        version="1.0.0-alpha1",
        packages=["view"],
        project_urls=data["project"]["urls"],
        package_dir={"": "src"},
        ext_modules=[
            Extension(
                "_view",
                glob("src/view/*.c"),
                include_dirs=["./include"],
            )
        ],
    )
