import os
from glob import glob

import toml
from setuptools import Extension, setup
from setuptools.command.build_py import build_py

with open("./README.md") as f:
    long_desc: str = f.read()

class build_py_with_pth_file(build_py):
    def run(self):
        super().run()

        dest = "view.pth"
        loc = "src/view/view.pth"

        out = os.path.join(self.build_lib, dest)
        self.copy_file(loc, out, preserve_mode=0)

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
            )
        ],
        include_dirs=["./include"],
        cmdclass={"build_py": build_py}
    )
