# Routing

## Route Objects

When you call any sort of router function (e.g. `get` or `post`), it takes in a parameter that is either a function or a `Route` object. If it's a function, it's then converted to a `Route`, and if not, it's left alone. This structure allows variant order of decorators. 

For example, the following both work just fine:

```py
@get("/")
@query("a", str)
async def route(a: str):
    ...
```


```py
@query("a", str)
@get("/")
async def route(a: str):
    ...
```

A `Route` object is a dataclass that contains the following attributes:

- `func`, the actual route function
- `path`, the path of the route (`None` if it uses path parts)
- `method`, enum containing the method of the route
- `inputs`, a list of `RouteInput` objects that are the inputs for the route
- `doc`, the description of the route
- `cache_rate`, how often to cache the route response. `-1` by default (never cache)
- `errors`, a dict of error handlers
- `extra_types`, extra types for inputs
- `parts`, path parts

`Route`

::: view.routing.Route
