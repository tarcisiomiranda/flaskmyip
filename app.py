#!flask/bin/python
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_tasks():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200
    else:
        return jsonify({'ip': request.environ['HTTP_X_FORWARDED_FOR']}), 200

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8000)
