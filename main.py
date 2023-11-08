import pickle
import re

from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')


class Jezdec:
    def __init__(self, jmeno, prijmeni, trida, nick, je_plavec, kanoe_kamarad):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.trida = trida
        self.nick = nick
        self.je_plavec = je_plavec
        self.kanoe_kamarad = kanoe_kamarad


jezdci = []

try:
    with open('data.pkl', 'rb') as f:
        jezdci = pickle.load(f)
except FileNotFoundError:
    jezdci = []


def save_data():
    with open('data.pkl', 'wb') as f:
        pickle.dump(jezdci, f)


@app.teardown_appcontext
def on_teardown_appcontext(exception=None):
    save_data()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', jezdci=jezdci)


@app.route('/registrace', methods=['GET', 'POST'])
def registrace():
    if request.method == 'GET':
        return render_template('registrace.html')

    if request.method == 'POST':
        nick = request.form.get("nick")
        je_plavec = request.form.get("je_plavec")
        kanoe_kamarad = request.form.get("kanoe_kamarad")
        jmeno = request.form.get("jmeno")
        prijmeni = request.form.get("prijmeni")
        trida = request.form.get("trida")

        if not re.match("^[a-zA-Z0-9]{2,20}$", nick):
            return "Přezdívka musí obsahovat 2 až 20 znaků, a může obsahovat pouze písmena a čísla.", 400

        if kanoe_kamarad and re.match("^[a-zA-Z0-9]{2,20}$", kanoe_kamarad):
            return "Přezdívka pro spolujezdce může obsahovat pouze 2 až 20 znaků a smí obsahovat pouze písmena a čísla.", 400

        if je_plavec != 'on':
            return "Musíte označit, zda jste plavec.", 400

        if any(jezdec.nick == nick for jezdec in jezdci):
            return "Tento nickname již existuje.", 400

        if kanoe_kamarad and not any(jezdec.nick == kanoe_kamarad for jezdec in jezdci):
            return "Druhý účastník neexistuje.", 400

        jezdci.append(Jezdec(jmeno, prijmeni, trida, nick, je_plavec, kanoe_kamarad))
        return redirect('/')


@app.route('/api/check-nickname', methods=['GET'])
def check_nickname():
    requested_nick = request.args.get('nick')
    if any(jezdec.nick == requested_nick for jezdec in jezdci):
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})


if __name__ == '__main__':
    app.run(host='localhost', port=8090)
