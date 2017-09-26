import base64
import errno
import os
import sys

from flask import (Flask, abort, make_response, redirect, render_template,
                   request)
from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField
from wtforms.validators import DataRequired

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

AUTH_PORT = 8000

if app.debug is True:
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
else:
    try:
        secret_key_path = os.path.join(THIS_DIR, 'secret_key')
        app.secret_key = open(secret_key_path, 'rb').read()
    except IOError as exc:
        if errno.ENOENT == exc.errno:
            print('authenticator.py cannot find {}.'.format(secret_key_path))
            print('Create it with \npython -c '
                  "'import os; print(os.urandom(32))' > {}".format(secret_key_path))
            sys.exit(1)
        raise exc


class LoginForm(Form):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    target = HiddenField('Target', validators=[DataRequired()])


def EncodeToken(user, password):
    return base64.b64encode(user + ':' + password)


def DecodeToken(token):
    auth_decoded = base64.b64decode(token)
    user, password = auth_decoded.split(':', 2)
    return user, password


def ValidUser(user, password):
    if user == 'admin':
        enc = EncodeToken(user, password)
        return enc


@app.route('/', methods=['GET'])
def authenticate():
    token = request.cookies.get('token')
    if token is None:
        abort(401)
    username, password = DecodeToken(token)
    if ValidUser(username, password) is not None:
        # Add headers to be authenticated with services
        resp = make_response()
        resp.headers['REMOTE_USER'] = username
        resp.headers['X-WEBAUTH-USER'] = username
        return resp
    abort(401)


@app.route('/login', methods=['GET', 'POST'])
def login():
    target = request.headers.get('X-Original-URI', '')
    form = LoginForm(target=target)
    if form.validate_on_submit():
        username = form.login.data
        password = form.password.data
        target = form.target.data
        auth_token = ValidUser(username, password)
        if auth_token:
            resp = make_response(redirect(target))

            secure = True if app.debug is False else False
            # Secure limits cookies to HTTPS traffic only.
            # HttpOnly prevents JavaScript from reading the cookie
            resp.set_cookie('token', auth_token,
                            secure=secure,
                            httponly=True,
                            )

            # Set headers that will be received by the service for this request
            resp.headers['REMOTE_USER'] = username
            resp.headers['X-WEBAUTH-USER'] = username
            resp.headers['X-Forwarded-User'] = username
            return resp
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(port=AUTH_PORT)
