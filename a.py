from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def Home():
    return "Hello, CS203"
if __name__ == "__main__":
    app.run(debug=True)
