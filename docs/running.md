# Running

## Serving

You can simply run a view app via the `view serve` command, but if you're like me and would rather to just use the `python3` command, that's just as easy.

With `view serve`, you must be in the working directory of your app (i.e. there's an `app.py`, `view.toml`, or something of the sort), but with `python3` (or your default Python command), all you need to do is execute the file with the `app.run()` in it.

### The Run Call

`app.run()` is a special method, since it acts differently depending on the context. When running your app via `view serve`, this method does nothing, due to the presence of a special environment variable.

When running programmatically (i.e. via `python3`), it's what calls `app.load()` in simple and filesystem loading.

For my more experienced Python dev's, it also handles the pesky `if __name__ == '__main__` via some Python black magic, so no need to worry about your app starting when importing from that file. Here's an example:

```py
from view import new_app

app = new_app()

if __name__ == '__main__':  # This is redundant!
    app.run()
```

## Specifying the location

If you used `view init`, a file called `app.py` should have been created for you with an `app` variable declared as a new app instance. By default, changing either of these will break the `view serve` command, since it's configured to look for an `app` variable in an `app.py` file.

If you go to your configuration, you may change this via the `app_path` setting:

!!! note "Note"
    
    This documentation will assume you use the `view.toml` configuration style.

```toml
[app]
app_path = "my_different_file.py:my_cool_app_name"
```

In the format above, you can see we specify the file name first, and then the variable name second, both separated by a colon in the middle.

## Fancy mode and hijacks

By default, view.py will hijack the server's logger and open a fancy interface that's much cooler to look at (especially if you're being watched by others).

You can disable this behaviour via the `hijack` and `fancy` settings:

```toml
[log]
hijack = false
fancy = false
```

!!! warning "Warning"

    Hijack mode must be enabled to use fancy mode.

