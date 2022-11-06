#!flask/bin/python
from flask import Flask, jsonify, request, redirect
from decouple import config
import os

amb = os.getenv('AMB', False)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_tasks():
    # print('---->', request.url_root)
    # print('---->', request.headers['Host'])
    if str(request.headers['Host']) == 'discord.pinkserver.net':
        return redirect('https://discord.gg/SRK5eSrR', code=302)

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200
    else:
        return jsonify({'ip': request.environ['HTTP_X_FORWARDED_FOR']}), 200
    
    # return redirect("http://www.example.com", code=302)

@app.route('/home', methods=['GET'])
def home_ip():
    # URI params
    get_ip = request.args.get('g_ip')
    new_ip = request.args.get('n_ip')
    passwd = request.args.get('pass')

    if get_ip == config('PASSWD', default=False):
        with open('home_ip.txt', 'r') as file:
            n_ip = file.read()
            file.close()

        return n_ip

    if new_ip and passwd == config('PASSWD', default=False):
        with open('home_ip.txt', 'w') as file:
            file.write(new_ip)
            file.close()

        return 'Tudo OK! {}'.format(new_ip)

    else:
        return 'Oh my God!'

@app.route('/doidera/<string:name>/<int:age>')
def with_url_variables(name: str, age: int):
    # http://192.168.29.12:8000/home?name=Tarcisio&amp;age=28
    return jsonify(message="My name is " + name + " and I am " + str(age) + " years old")

if __name__ == '__main__':
    if amb:
        app.run(host='0.0.0.0', port=8000)
    else:
        app.run(debug=True,host='0.0.0.0', port=8000)
