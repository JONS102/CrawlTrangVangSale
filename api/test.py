from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Hello from Vercel!', 'status': 'success'})

@app.route('/health')
def health():
    return jsonify({'status': 'OK', 'message': 'Application is running'})

if __name__ == '__main__':
    app.run()
