# Project Creation

## Automatic

The View CLI supports automatically creating a project via the `view init` command.

```
$ view init
Path to initialize to [./]:
Loader strategy (manual, filesystem, simple) [filesystem]:
Created `view.toml`
Created `app.py`
Created `pyproject.toml`
Created `scripts`
Created `routes`
Created `routes/index.py`
Successfully initalized app in `/path/omitted`
```

The loader strategy is related to routing, which you will learn more about later.

## Manually

view.py doesn't actually need any big project structure. In fact, you can run an app in just a single Python file, but larger structures like this might be more convenient for big projects. The only real requirement for something to be a view app is that it calls `new_app`, but again, more on that later.

## Structure

Generally, you're going to want one of the configuration files talked about earlier, but if you're against more configuration files that's OK.
