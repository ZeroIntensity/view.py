# WebSockets

!!! question "What is a WebSocket?"

    In web development, a WebSocket is a two-way communication channel used on websites. Read more about them [here](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API).

## WebSocket Routers

Like other routers, the `websocket` router has both a standard and direct variation, with the same API. Unlike other routers, a WebSocket comes with one input out of the box, that being the actual WebSocket object.

!!! danger "Other Inputs"

    You can add `query` inputs and path parameters to a `websocket` route, but not a `body` input.

A WebSocket route does also not care what you return. In fact, a type checker expects that routes decorated with `websocket` return `None`.

For example, a WebSocket that does nothing is as follows:

```py
from view import new_app, WebSocket

app = new_app()

@app.websocket("/")
async def websocket_route(ws: WebSocket):
    ...

app.run()
```

!! warning

    If you installed `uvicorn` manually, make sure to install `websockets` or `wsproto` if you plan on using WebSockets:

    ```
    $ pip install websockets
    ```

## Handshakes

If you used the above code, it wouldn't actually work as a WebSocket from the client, since we don't accept the connection.

Like other libraries, view.py does not automatically decide the lifecycle of your WebSocket handshake, meaning you have to manually `accept` and `close` it. For example, adding on to our above example that does nothing:

```py
from view import new_app, WebSocket

app = new_app()

@app.websocket("/")
async def websocket_route(ws: WebSocket):
    await ws.accept()
    await ws.close()

app.run()
```

Now, we could actually use a WebSocket client to access this route. However, you should use a context manager instead of manually calling lifecycle methods:

```py
from view import new_app, WebSocket

app = new_app()

@app.websocket("/")
async def websocket_route(ws: WebSocket):
    async with ws:
        ...

app.run()
```

!!! note Client Disconnect

    A `WebSocketHandshakeError` is raised if the client disconnects before the server calls `close`.

## Sending and Receiving

Now, let's make our WebSocket do something! We can use `send` and `receive` to send and receive data.

The best way to understand these methods is visually, so a simple chat application could look like:

```py
from view import new_app, WebSocket
import aiofiles  # For asynchronous input()

app = new_app()

@app.websocket("/")
async def websocket_route(ws: WebSocket):
    await ws.accept()  # We shouldn't ever need to exit, so no need for a context manager
    while True:
        await ws.send(await aiofiles.stdin.readline())
        print("Them:", await ws.receive())

app.run()
```

### Receiving Types

Using view.py's type-casting system, you can specify a type to receive from the client by passing `tp` to `receive`. The supported types are:

-   `str`
-   `int`
-   `bool`
-   `bytes`
-   `dict`

For example, if you wanted to receive JSON data:

```py
from view import new_app, WebSocket

app = new_app()

@app.websocket("/")
async def websocket_route(ws: WebSocket):
    async with ws:
        json = await ws.receive(tp=dict)

app.run()
```

## Message Pairs

In many cases, such as with our chat app from above, we want a 1:1 ratio of messages from the server to the client. view.py gives you the `pair` method, to remove some boilerplate. It simply sends a message, then returns a received message. For example, with our chat app from above:

```py
from view import new_app, WebSocket
import aiofiles

app = new_app()

@app.websocket("/")
async def websocket_route(ws: WebSocket):
    await ws.accept()
    while True:
        print("Them:", await ws.pair(await aiofiles.stdin.readline()))

app.run()
```

As stated above, `pair` sends the message before receiving, but you can reverse this by passing `recv_first=True`:

```py
print("Them:", await ws.pair(await aiofiles.stdin.readline(), recv_first=True))
```

This would receive from the client, _then_ send a message, and then return that received message.

## Expecting Messages

In some cases, you might just want the client to send some data to ensure compliance with a protocol, or perhaps for a [ping-pong](https://en.wikipedia.org/wiki/Ping-pong_scheme). You can use the `expect` method, which ensures that the client send some data, and then discards the message. For example:

```py
from view import new_app, WebSocket

app = new_app()

@app.websocket("/")
async def websocket_route(ws: WebSocket):
    async with ws:
        await ws.expect("MYPROTOCOL V1.1")
        await ws.send("ACK")
        # ...

app.run()
```

## Review

WebSocket routes always have at least one route input, that being a `WebSocket` object representing the connection. view.py does not handle the connection lifetime, so calling `accept`, `close`, or using the context manager is up to the user.

Data can be sent and received via `send` and `receive` (who would have guessed!), and certain types can be expected from the client via the `tp` parameter. You can also use the `pair` method to eliminate some boilerplate when it comes to 1:1 message correspondence, as well as use the `expect` method to expect that the client sends some data.
