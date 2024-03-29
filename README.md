# NGINX Auth Proxy

## Problem

You have multiple services running on the same server on different ports or subdomains.
You want passwords to validate against one source of truth.
You want to use the same authentication (login and password) for every service without having to login to each one (Single Sign On).

## How it works

Services are running locally on a specific port. For example JupyterHub is running on port 9000 internally.
Auth Service is running on port 8000 internally. It can be a Python webserver or anything else as long as it is running on port 8000 internally.

Each request needs to have an auth token, which will be checked by the auth service.
If the auth token is valid, route the request to the internal service (ex. port 9000), passing the auth token and any additional headers.
If no auth token is provided or the token is not valid then the request will be sent to the auth service login form.

When you login to the auth service it will provide an auth token which will be used for subsequent requests.

![Step 1](https://raw.githubusercontent.com/siecje/nginx-auth-proxy/master/notes/first.png)

![Step 2](https://raw.githubusercontent.com/siecje/nginx-auth-proxy/master/notes/second.png)

![Step 3](https://raw.githubusercontent.com/siecje/nginx-auth-proxy/master/notes/third.png)

Using the `ngx_http_auth_request_module` with LDAP authentication is described in this article https://www.nginx.com/blog/nginx-plus-authenticate-users/.

## Adding a new service

- Add the nginx config to run the service locally on an available port.

- Configure the new service to authenticate via `REMOTE_USER` or
add the required headers for the service to `authenticator.py` and `include.d/application.include`.

- Restart `nginx` to reload the nginx configuration.

## Run demo

You will need NGINX with the [ngx_http_auth_request_module](http://nginx.org/en/docs/http/ngx_http_auth_request_module.html) installed.

```shell
sudo apt-get install nginx-full
```

```shell
git clone https://github.com/Siecje/nginx-auth-proxy
cd nginx-auth-proxy
```

### Simulate subdomains locally

This will resolve both `one.localhost` and `two.localhost` to `localhost`.

```shell
echo "127.0.0.1 one.localhost" | sudo tee -a /etc/hosts
echo "127.0.0.1 two.localhost" | sudo tee -a /etc/hosts
```

### Create self signed certificate

```shell
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'
sudo mv cert.pem /etc/ssl/certs/
sudo mv key.pem /etc/ssl/certs/
```

### Configure nginx

```shell
sudo rm /etc/nginx/sites-enabled/default
sudo mkdir /etc/nginx/include.d/
```

```shell
sudo ln -s `pwd`/include.d/authentication.include /etc/nginx/include.d/authentication.include
sudo ln -s `pwd`/include.d/application.include /etc/nginx/include.d/application.include
```

```shell
sudo ln -s `pwd`/conf.d/authenticator.conf /etc/nginx/conf.d/authenticator.conf
sudo ln -s `pwd`/conf.d/service1.conf /etc/nginx/conf.d/service1.conf
sudo ln -s `pwd`/conf.d/service2.conf /etc/nginx/conf.d/service2.conf
```

```shell
sudo service nginx restart
```

### Start services

```shell
python -m venv venv
venv/bin/python -m pip install pip setuptools wheel --upgrade
venv/bin/python -m pip install -r requirements.txt
```

```shell
venv/bin/python authenticator.py &
venv/bin/python service1.py &
venv/bin/python service2.py &
```

When you visit `http://one.localhost/` you will be redirected to `http://one.localhost/` and need to login.
As long as you use the username 'admin' you will be able to access the service.

You will then be able to visit `https://two.localhost` and login with the same username and password.

## Run in production

- [ ] Implement the authentication logic in `valid_user()` in `authenticator.py`.

- [ ] Create secret_key file

  - python -c 'import os; print(os.urandom(32))' > secret_key

- [ ] Add HTTPS certificate to `include.d/certificate.include`
