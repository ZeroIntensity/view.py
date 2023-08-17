import os
import shutil
import sysconfig
from contextlib import suppress
from glob import glob

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl
from setuptools._distutils.ccompiler import new_compiler


class CustomBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, _: str, data: dict):
        self.clean()
        c = new_compiler()
        c.define_macro("PY_SSIZE_T_CLEAN")
        c.add_include_dir(sysconfig.get_path("include"))
        c.add_include_dir("./include")
        c.compile(
            glob("./src/_view/*.c"),
            "./ext/obj",
            extra_preargs=["-fPIC", "-v"] if os.name != "nt" else [],
            debug=True,
        )

        files = []

        for root, dir, fls in os.walk("./ext/obj"):
            for i in fls:
                if (i.endswith(".o")) or (i.endswith(".obj")):
                    files.append(os.path.join(root, i))

        c.link_shared_lib(files, "_view", "./ext/lib", debug=True)

        with suppress(KeyError):
            data["force_include"][
                os.path.join("./ext/lib", "lib_view.so")
            ] = "./src/_view.so"

        with suppress(KeyError):
            data["infer_tag"] = True

        with suppress(KeyError):
            data["pure_python"] = False

    def clean(self, *_):
        path = os.path.join(self.root, "ext")
        if os.path.exists(path):
            shutil.rmtree(path)


@hookimpl
def hatch_register_build_hook():
    return CustomBuildHook
