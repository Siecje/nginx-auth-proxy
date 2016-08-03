import base64

from flask import Flask, abort, make_response, render_template, request
from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

AUTH_PORT = 8000


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
    token = request.headers.get('token')
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


@app.route('/login/', methods=["GET", "POST"])
def login():
    target = request.headers.get('X-Target', "")
    print 'Target: ' + target
    form = LoginForm(target = target)
    if form.validate_on_submit():
        print 'inside'
        username = form.login.data
        password = form.password.data
        target = form.target.data
        auth_token = ValidUser(username, password)
        if auth_token:
            resp = make_response()
            resp.set_cookie('token', auth_token)
            print "before target"
            print target
            resp.headers['Location'] = target
            return resp
    return render_template('login.html', form=form)


if __name__ == "__main__":
    app.run(port = AUTH_PORT)
