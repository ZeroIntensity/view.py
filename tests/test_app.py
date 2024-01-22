from dataclasses import dataclass, field
from typing import Dict, List, NamedTuple, TypedDict, Union
import attrs
from pydantic import BaseModel, Field
from typing_extensions import NotRequired
from ward import test

from view import BodyParam, Response, body, new_app, query


@test("responses")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return "hello"

    async with app.test() as test:
        assert (await test.get("/")).message == "hello"


@test("status codes")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return "error", 400

    async with app.test() as test:
        res = await test.get("/")
        assert res.status == 400
        assert res.message == "error"


@test("headers")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return "hello", {"a": "b"}

    async with app.test() as test:
        res = await test.get("/")
        assert res.headers["a"] == "b"
        assert res.message == "hello"


@test("combination of headers, responses, and status codes")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return 201, "123", {"a": "b"}

    async with app.test() as test:
        res = await test.get("/")
        assert res.status == 201
        assert res.message == "123"
        assert res.headers["a"] == "b"


@test("result protocol")
async def _():
    app = new_app()

    class MyObject:
        def __view_result__(self):
            return "hello", 200

    @app.get("/")
    async def index():
        return MyObject()

    @app.get("/multi")
    async def multi():
        return Response(MyObject(), 201)

    async with app.test() as test:
        assert (await test.get("/")).message == "hello"
        res = await test.get("/multi")
        assert res.message == "hello"
        assert res.status == 201


@test("body type validation")
async def _():
    app = new_app()

    @app.get("/")
    @body("name", str)
    async def index(name: str):
        return name

    @app.get("/status")
    @body("status", int)
    async def stat(status: int):
        return "hello", status

    @app.get("/union")
    @body("test", bool, int)
    async def union(test: Union[bool, int]):
        if type(test) is bool:
            return "1"
        elif type(test) is int:
            return "2"
        else:
            raise Exception

    @app.get("/multi")
    @body("status", int)
    @body("name", str)
    async def multi(status: int, name: str):
        return name, status

    async with app.test() as test:
        assert (await test.get("/", body={"name": "hi"})).message == "hi"
        assert (await test.get("/status", body={"status": 404})).status == 404
        assert (
            await test.get("/status", body={"status": "hi"})
        ).status == 400  # noqa
        assert (await test.get("/union", body={"test": "a"})).status == 400
        assert (
            await test.get("/union", body={"test": "true"})
        ).message == "1"  # noqa
        assert (await test.get("/union", body={"test": "2"})).message == "2"
        res = await test.get("/multi", body={"status": 404, "name": "test"})
        assert res.status == 404
        assert res.message == "test"


@test("query type validation")
async def _():
    app = new_app()

    @app.get("/")
    @query("name", str)
    async def index(name: str):
        return name

    @app.get("/status")
    @query("status", int)
    async def stat(status: int):
        return "hello", status

    @app.get("/union")
    @query("test", bool, int)
    async def union(test: Union[bool, int]):
        if type(test) is bool:
            return "1"
        elif type(test) is int:
            return "2"
        else:
            raise Exception

    @app.get("/multi")
    @query("status", int)
    @query("name", str)
    async def multi(status: int, name: str):
        return name, status

    async with app.test() as test:
        assert (await test.get("/", query={"name": "hi"})).message == "hi"
        assert (await test.get("/status", query={"status": 404})).status == 404
        assert (
            await test.get("/status", query={"status": "hi"})
        ).status == 400  # noqa
        assert (await test.get("/union", query={"test": "a"})).status == 400
        assert (
            await test.get("/union", query={"test": "true"})
        ).message == "1"  # noqa
        assert (await test.get("/union", query={"test": "2"})).message == "2"
        res = await test.get("/multi", query={"status": 404, "name": "test"})
        assert res.status == 404
        assert res.message == "test"


@test("queries directly from app and body")
async def _():
    app = new_app()

    @app.query("name", str)
    @app.get("/")
    async def query_route(name: str):
        return name

    @app.get("/body")
    @app.body("name", str)
    async def body_route(name: str):
        return name

    async with app.test() as test:
        assert (await test.get("/", query={"name": "test"})).message == "test"
        assert (
            await test.get("/body", body={"name": "test"})
        ).message == "test"


@test("response type")
async def _():
    app = new_app()

    @app.get("/")
    async def index():
        return Response("hello world", 201, {"hello": "world"})

    async with app.test() as test:
        res = await test.get("/")

        assert res.message == "hello world"
        assert res.status == 201
        assert res.headers["hello"] == "world"


@test("object validation")
async def _():
    app = new_app()

    @dataclass
    class Dataclass:
        a: str
        b: Union[str, int]
        c: Dict[str, int]
        d: dict = field(default_factory=dict)

    class Pydantic(BaseModel):
        a: str
        b: Union[str, int]
        c: Dict[str, int]
        d: dict = Field(default_factory=dict)

    class ND(NamedTuple):
        a: str
        b: Union[str, int]
        c: Dict[str, int]

    class VB:
        __view_body__ = {
            "hello": str,
            "world": BodyParam((str, int), default="hello"),
        }

        @staticmethod
        def __view_construct__(hello: str, world: Union[str, int]):
            assert isinstance(hello, str)
            assert world == "hello"

    class TypedD(TypedDict):
        a: str
        b: Union[str, int]
        c: Dict[str, int]
        d: NotRequired[str]

    @app.get("/td")
    @app.query("data", TypedD)
    async def td(data: TypedD):
        assert data["a"] == "1"
        assert data["b"] == 2
        assert data["c"]["3"] == 4
        assert "d" not in data
        return "hello"

    @app.get("/dc")
    @app.query("data", Dataclass)
    async def dc(data: Dataclass):
        assert data.a == "1"
        assert data.b == 2
        assert data.c["3"] == 4
        assert data.d == {}
        return "hello"

    @app.get("/pd")
    @app.query("data", Pydantic)
    async def pd(data: Pydantic):
        assert data.a == "1"
        assert data.c["3"] == 4
        assert data.d == {}
        return "world"

    @app.get("/nd")
    @app.query("data", ND)
    async def nd(data: ND):
        assert data.a == "1"
        assert data.b == 2
        assert data.c["3"] == 4
        return "foo"

    @app.get("/vb")
    @app.query("data", VB)
    async def vb(data: VB):
        return "yay"

    class NestedC(NamedTuple):
        c: Union[str, int]

    class NestedB(NamedTuple):
        b: NestedC

    class NestedA(NamedTuple):
        a: NestedB

    @app.get("/nested")
    @app.query("data", NestedA)
    async def nested(data: NestedA):
        assert data.a.b.c in {"hello", 1}
        return "hello"

    async with app.test() as test:
        assert (
            await test.get(
                "/td", query={"data": {"a": "1", "b": 2, "c": {"3": 4}}}
            )
        ).message == "hello"
        assert (
            await test.get(
                "/dc", query={"data": {"a": "1", "b": 2, "c": {"3": 4}}}
            )
        ).message == "hello"
        assert (
            await test.get(
                "/pd", query={"data": {"a": "1", "b": 2, "c": {"3": 4}}}
            )
        ).message == "world"
        assert (
            await test.get(
                "/nd", query={"data": {"a": "1", "b": 2, "c": {"3": 4}}}
            )
        ).message == "foo"
        assert (
            await test.get(
                "/pd", query={"data": {"a": "1", "b": 2, "c": {"3": "4"}}}
            )
        ).status == 200
        assert (
            await test.get("/vb", query={"data": {"hello": "world"}})
        ).message == "yay"
        assert (
            await test.get("/vb", query={"data": {"hello": 2}})
        ).status == 400
        assert (
            await test.get(
                "/vb", query={"data": {"hello": "world", "world": {}}}
            )
        ).status == 400
        assert (
            await test.get(
                "/nested", query={"data": {"a": {"b": {"c": "hello"}}}}
            )
        ).message == "hello"
        assert (
            await test.get("/nested", query={"data": {"a": {"b": {"c": 1}}}})
        ).message == "hello"
        assert (
            await test.get(
                "/dc", query={"data": {"a": "1", "b": True, "c": {"3": 4}}}
            )
        ).status == 400


@test("dict validation")
async def _():
    app = new_app()

    class Object(NamedTuple):
        a: str
        b: Union[str, int]

    @app.get("/")
    @app.query("data", Dict[str, Object])
    async def index(data: Dict[str, Object]):
        assert data["a"].a == "a"
        assert data["b"].b in {"a", 1}
        return "hello"

    async with app.test() as test:
        assert (
            await test.get(
                "/",
                query={"a": {"a": "a", "b": "b"}, "b": {"a": "a", "b": "a"}},
            )
        ).message


@test("non async routes")
async def _():
    app = new_app()

    @app.get("/")
    def index():
        return "hello world", 201, {"a": "b"}

    async with app.test() as test:
        res = await test.get("/")

        assert res.message == "hello world"
        assert res.status == 201
        assert res.headers["a"] == "b"


@test("list validation")
async def _():
    app = new_app()

    @app.get("/")
    @app.query("test", List[int])
    async def index(test: List[int]):
        return str(test[0])

    @app.get("/union")
    @app.query("test", List[Union[int, str]])
    async def union(test: List[Union[int, str]]):
        return str(test[0])

    @app.get("/dict")
    @app.query("test", Dict[str, List[str]])
    async def d(test: Dict[str, List[str]]):
        return test["a"][0]

    @dataclass
    class Body:
        l: List[int]
        d: Dict[str, List[str]]

    @app.get("/body")
    @app.body("test", Body)
    async def bod(test: Body):
        return test.d["a"][0], test.l[0]

    @dataclass
    class B:
        test: str

    @dataclass
    class A:
        l: List[B]

    @app.get("/nested")
    @app.body("test", A)
    async def nested(test: A):
        return test.l[0].test

    async with app.test() as test:
        assert (await test.get("/", query={"test": [1, 2, 3]})).message == "1"
        assert (
            await test.get("/union", query={"test": [1, "2", 3]})
        ).message == "1"
        assert (
            await test.get("/", query={"test": [1, "2", True]})
        ).status == 400
        assert (
            await test.get("/dict", query={"test": {"a": ["1", "2", "3"]}})
        ).message == "1"
        assert (
            await test.get("/dict", query={"test": {"a": ["1", "2", 3]}})
        ).status == 400
        assert (
            await test.get(
                "/body",
                body={"test": {"l": [200], "d": {"a": ["1", "2", "3"]}}},
            )
        ).message == "1"
        assert (
            await test.get(
                "/body",
                body={"test": {"l": [200], "d": {"a": ["1", "2", 3]}}},
            )
        ).status == 400
        assert (
            await test.get(
                "/nested",
                body={"test": {"l": [{"test": "1"}]}},
            )
        ).message == "1"
        assert (
            await test.get(
                "/nested",
                body={"test": {"l": [{"test": 2}]}},
            )
        ).status == 400


@test("auto route inputs")
async def _():
    @dataclass()
    class Data:
        a: str
        b: int

    app = new_app()

    @app.get("/")
    async def index(name: str, status: int):
        return name, status

    @app.get("/merged")
    @query("status", int)
    async def merged(name: str, status: int):
        return name, status

    @app.get("/data")
    async def test_data(data: Data):
        return data.a, data.b

    async with app.test() as test:
        res = await test.get("/", query={"name": "hi", "status": 201})
        assert res.message == "hi"
        assert res.status == 201

        res2 = await test.get("/merged", query={"name": "hi", "status": 201})
        assert res2.message == "hi"
        assert res2.status == 201

        res3 = await test.get("/data", query={"data": {"a": "hi", "b": 201}})
        assert res3.message == "hi"
        assert res3.status == 201

@test("attrs validation")
async def _():
    app = new_app()
    
    @attrs.define
    class Test:
        a: str
        b: int
        c: List[str]
        d: Dict[str, int] = attrs.Factory(dict)

    @app.get("/")
    @app.query("test", Test)
    async def index(test: Test):
        return test.a

    async with app.test() as test:
        assert (await test.get("/", query={"test": {"a": "b", "b": 0, "c": []}})).message == "b"
        assert (await test.get("/", query={"test": {"a": "b", "b": "hi", "c": []}})).status == 400
        assert (await test.get("/", query={"test": {"a": "b", "b": 0, "c": ["a"]}})).message == "b"
        assert (await test.get("/", query={"test": {"a": "b", "b": 0, "c": [1]}})).status == 400
        assert (await test.get("/", query={"test": {"a": "b", "b": 0, "c": [], "d": {"a": "b"}}})).status == 400
        assert (await test.get("/", query={"test": {"a": "b", "b": 0, "c": [], "d": {"a": 0}}})).message == "b"

@test("synchronous route inputs")
async def _():
    app = new_app()

    @app.get("/")
    @app.query("test", str)
    def index(test: str):
        return test

    @app.get("/body")
    @app.body("test", str)
    def bd(test: str):
        return test

    @app.get("/both")
    @app.body("a", str)
    @app.query("b", str)
    def both(a: str, b: str):
        return a + b

    async with app.test() as test:
        assert (await test.get("/", query={"test": "a"})).message == "a"
        assert (await test.get("/body", body={"test": "b"})).message == "b"
        assert (await test.get("/both", body={"a": "a"}, query={"b": "b"})).message == "ab"
