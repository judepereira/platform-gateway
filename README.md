# Asyncy Server

API gateway server for executing Stories via HTTP/TCP/WebSockets.

```coffee
http-endpoint method:get path:'/' as request, response
    response.write data:'Hello World'
    response.status code:200
    response.finish
```

```sh
curl https://foobar.asyncyapp.com
>>> Hello World
```


## Development

Setup virtual environment and install dependancies
```
virtualenv -p python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
```

Run locally by calling

```
python -m app.main --logging=debug --debug --engine=engine:50051
```
> Assuming the Asyncy Engine is at `engine:50051`
