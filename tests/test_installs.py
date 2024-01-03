from versions import parse_version
from ward import raises, test

from view import __version__, new_app
from view.install import check_dep, ensure_dep, needs


@test("dependency checking")
def _():
    version = parse_version(__version__)
    v = version.next_minor()
    assert check_dep("view.py")
    assert not check_dep(f"view.py@{v.to_string()}")


@test("dependency installs")
async def _():
    await ensure_dep("pointers.py")
    import pointers


@test("needing installs")
async def _():
    app = new_app()
    await needs("hoist-http")
    import hoist
    app.config.auto_install = False

    with raises(ModuleNotFoundError):
        await needs("templates.py")
