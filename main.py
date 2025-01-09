from flask import Flask, request, jsonify

app = Flask(__name__)
commands = []

@app.route("/send", methods=["POST"])
def send_command():
    data = request.json
    command = data.get("command")
    if command:
        commands.append(command)
        return jsonify({"message": "received"}), 200
    return jsonify({"error": "no command"}), 400

@app.route("/get", methods=["GET"])
def get_commands():
    global commands
    response = commands
    commands = []
    return jsonify({"commands": response}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
