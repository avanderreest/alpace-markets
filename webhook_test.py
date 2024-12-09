from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Connected, goed zo"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        content = request.json
        print(content)
        return jsonify(content), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)