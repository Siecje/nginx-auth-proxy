from flask import Flask, request


app = Flask(__name__)

PORT = 9000

@app.route('/', methods=["GET"])
def home():
    remote_user = request.headers.get('REMOTE_USER')
    return "Hello {}, this is the service1.".format(remote_user)


if __name__ == "__main__":
    app.run(port=PORT, debug=True)
