# Uvify
Instant python environments from github links with <a href="https://gitingest.com/">GitIngest</a> and <a href="https://github.com/astral-sh/uv">uv</a> python manager.
Turn any GitHub repository to a uv command

> uv is by far the fastest python and package manager. 
<img src="assets/image.png">

<i>Source: https://github.com/astral-sh/uv</i>

## Using uvify CLI locally
Dog Fooding - uvify on uvify: 
```shell
uv run uvify https://github.com/psf/requests | jq 
{
  "oneLiner": "uv run --python '3.11' --with 'certifi>=2017.4.17,charset_normalizer>=2,<4,idna>=2.5,<4,urllib3>=1.21.1,<3,requests' python -c 'import requests;print(requests.__version__)'",
  "uvInstallFromSource": "uv run --with 'git+https://github.com/psf/requests' --python '3.11' python",
  "dependencies": [
    "certifi>=2017.4.17",
    "charset_normalizer>=2,<4",
    "idna>=2.5,<4",
    "urllib3>=1.21.1,<3"
  ],
  "packageName": "requests",
  "pythonVersion": "3.11"
}
```

## Using the FastAPI application and HTTP client
```shell
# Run the server
uv run uvicorn src.uvify:api --host 0.0.0.0 --port 8000

# Using curl
curl http://0.0.0.0:8000/psf/requests | jq

# Using wget
wget -O-  http://0.0.0.0:8000/psf/requests | jq .oneLiner
```


## Developing
```shell
# Install dependencies
uv venv
uv sync --dev
uv run pytest

# Install editable version
uv run pip install --editable .
uv run uvify psf/requests

# Run the HTTP API with reload
uv run uvicorn src.uvify:api --host 0.0.0.0 --port 8000 --reload 
curl http://0.0.0.0:8000/psf/requests | jq
```

# Thanks 
Thanks to the UV team and Astral for this amazing tool.