from flask import Flask, request


app = Flask(__name__)

PORT = 7000

@app.route('/', methods=["GET"])
def home():
    remote_user = request.headers.get('REMOTE_USER')
    return "Hello {}, this is service2.".format(remote_user)


if __name__ == "__main__":
    app.run(port=PORT, debug=True)
