# Asyncy Server

Gateway and proxy for executing Stories via HTTP/TCP/WebSockets.

```coffee
http method:get path:'/' as request, response
  res write data:'Hello World'
```

```sh
curl https://foobar.asyncyapp.com
>>> Hello World
```


## Development

Run locally by having the Engine running and call

```
DEBUG=1 CONFIG_DIR=$PWD ENGINE=localhost:50051 python -m app.main --logging=debug
```
