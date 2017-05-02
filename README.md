# NGINX Auth Proxy

## Problem

You have multiple services running on the same server on different ports or subdomains.
You want to use the same authentication (login and password) for every service without having to login to each one (Single Sign On).
You want passwords to validate against one source of truth.

## How does it work

Service (think JupyterHub) is running on port 9000 internally.
Auth Service (Python server) running on port 8000 internally.

Each request needs to have an auth token, which will be checked by the auth service.
If no auth token is provided or the token is not valid then the request will be sent to the auth service login form.
If auth token is valid route to the internal service (ex. port 9000), passing the auth token and all additional headers required by all services.

When you login to the auth service it will provide an auth token which will be used for subsequent requests.

[Diagram](https://github.com/Siecje/nginx-auth-proxy/blob/master/steps.md)

## Adding a new service

- Add the nginx config to run the service locally on an available port.

- Configure the new service to authenticate via `REMOTE_USER` or
add the required headers for the service to `authenticator.py` and `nginx.conf`.

- Restart `nginx` to reload the nginx configuration.

## Running

You will need NGINX with the [ngx_http_auth_request_module](http://nginx.org/en/docs/http/ngx_http_auth_request_module.html) installed.

```shell
sudo apt-get install nginx-full
```

```shell
git clone https://github.com/Siecje/nginx-auth-proxy
cd nginx-auth-proxy
```

```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

```shell
sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx_backup.conf
sudo ln -s nginx.conf /etc/nginx/nginx.conf
```

```shell
python authenticator.py &
python service.py &
```

```shell
sudo service nginx restart
```

When you visit `http://localhost:8081` you will need to login.
As long as you use the username 'admin' you will be able to access the service.
