import pickle
import re

from flask import Flask, render_template, request, jsonify, redirect, session

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
app.secret_key = 'leaslRXVmy'


class Jezdec:
    def __init__(self, uzivatelske_jmeno, heslo, jmeno, prijmeni, trida, plavec):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.trida = trida
        self.uzivatelske_jmeno = uzivatelske_jmeno
        self.heslo = heslo
        self.plavec = plavec
        self.spolujezdec = None
        self.pozvanky = []

    def smazat_jezdce(self):
        if self.spolujezdec:
            jezdec_spolujezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == self.spolujezdec),
                                      None)
            jezdec_spolujezdec.spolujezdec = None
            odebrat_lodku(self.uzivatelske_jmeno)
        jezdci.remove(self)

        return redirect('/odhlaseni'), 302

    def poslat_pozvanku(self, spolujezdec):
        if self.spolujezdec:
            return jsonify({'error': 'Máte již spolujezdce, nelze odeslat pozvánku.'}), 400

        if self.uzivatelske_jmeno == spolujezdec:
            return jsonify({'error': 'Nemůžete poslat pozvánku sobě.'}), 400

        jezdec_spolujezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == spolujezdec), None)

        if not jezdec_spolujezdec:
            return jsonify({'error': 'Uživatel neexistuje.'}), 400

        if self.uzivatelske_jmeno in jezdec_spolujezdec.pozvanky:
            return jsonify({'error': 'Tomuto jezdci již byla pozvánka odeslána.'}), 400

        jezdec_spolujezdec.pozvanky.append(self.uzivatelske_jmeno)
        return jsonify({'success': 'Pozvánka byla úspěšně odeslána.'}), 200

    def prijmout_pozvanku(self, odesilatel):
        jezdec_odesilatel = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == odesilatel), None)

        self.pozvanky.remove(jezdec_odesilatel.uzivatelske_jmeno)

        if jezdec_odesilatel.spolujezdec:
            return jsonify({'error': 'Uživatel již má spolujezdce.'}), 400

        self.spolujezdec = jezdec_odesilatel.uzivatelske_jmeno
        jezdec_odesilatel.spolujezdec = self.uzivatelske_jmeno
        self.pozvanky.clear()
        jezdec_odesilatel.pozvanky.clear()
        lodky.append(Lodka([self.uzivatelske_jmeno, jezdec_odesilatel.uzivatelske_jmeno]))
        return jsonify({'success': 'Pozvánka byla úspěšně přijata.'}), 200

    def odmitnout_pozvanku(self, odesilatel):
        self.pozvanky.remove(odesilatel)
        return jsonify({'success': 'Pozvánka byla úspěšně odmítnuta.'}), 200


class Lodka:
    def __init__(self, jezdci):
        self.jezdci = jezdci

    def je_jezdec(self, jezdec):
        if jezdec in self.jezdci:
            return True
        return False


def odebrat_lodku(jezdec):
    for lodka in lodky:
        if lodka.je_jezdec(jezdec):
            lodky.remove(lodka)
            return True
    return False


jezdci = []
lodky = []
tridy = ['A1', 'E1', 'C1a', 'C1b', 'C1c', 'A2', 'E2', 'C2a', 'C2b', 'C2c', 'A3', 'E3', 'C3a', 'C3b', 'C3c', 'A4', 'E4',
         'C4a', 'C4b', 'C4c']

try:
    with open('data_jezdci.pkl', 'rb') as f_jezdci:
        jezdci = pickle.load(f_jezdci)
except FileNotFoundError:
    jezdci = []

try:
    with open('data_lodky.pkl', 'rb') as f_lodky:
        lodky = pickle.load(f_lodky)
except FileNotFoundError:
    lodky = []


def ulozit_jezdce():
    with open('data_jezdci.pkl', 'wb') as f:
        pickle.dump(jezdci, f)


def ulozit_lodky():
    with open('data_lodky.pkl', 'wb') as f:
        pickle.dump(lodky, f)


@app.teardown_appcontext
def on_teardown_appcontext(exception=None):
    ulozit_jezdce()
    ulozit_lodky()


@app.route('/', methods=['GET'])
def index():
    if 'uzivatelske_jmeno' in session:
        return redirect('/jezdec'), 302
    return render_template('index.html'), 200


@app.route('/registrace', methods=['GET', 'POST'])
def registrace():
    if request.method == 'GET':
        if 'uzivatelske_jmeno' in session:
            return redirect('/jezdec'), 302
        return render_template('registrace.html', tridy=tridy), 200

    if request.method == 'POST':
        data = request.json
        uzivatelske_jmeno = data.get("uzivatelske_jmeno")
        heslo = data.get("heslo")
        jmeno = data.get("jmeno")
        prijmeni = data.get("prijmeni")
        trida = data.get("trida")
        plavec = data.get("plavec")

        if uzivatelske_jmeno is None or not re.match("^[a-z0-9]{2,40}$", uzivatelske_jmeno):
            return jsonify({
                'error': 'Uživatelské jméno musí obsahovat 2 až 40 znaků, a může obsahovat pouze malá písmena a čísla.'}), 400

        if any(jezdec.uzivatelske_jmeno == uzivatelske_jmeno for jezdec in jezdci):
            return jsonify({
                'error': 'Toto uživatelské jméno již někdo používá.'}), 400

        if heslo is None or not re.match(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~`!@#$%^&*()_+\-={[}\]|:;"\'<>,.?/])[A-Za-z\d~`!@#$%^&*()_+\-={[}\]|:;"\'<>,.?/]{8,}$',
                heslo):
            return jsonify({
                'error': 'Heslo musí obsahovat alespoň jedno malé písmeno, jedno velké písmeno, jednu číslici a jeden speciální znak. Délka hesla musí být minimálně 8 znaků.'}), 400

        if jmeno is None or not re.match(r'^[A-Ž][a-ž]{1,29}', jmeno):
            return jsonify({
                'error': 'Jméno musí obsahovat pouze 2 až 30 znaků a smí obsahovat pouze písmena a začáteční písmeno musí být velké.'}), 400

        if prijmeni is None or not re.match(r'^[A-Ž][a-ž]{1,39}', prijmeni):
            return jsonify({
                'error': 'Příjmení musí obsahovat pouze 2 až 40 znaků a smí obsahovat pouze písmena a začáteční písmeno musí být velké.'}), 400

        if trida is None or trida not in tridy:
            return jsonify({'error': 'Třída neexistuje.'}), 400

        if any(jezdec.jmeno == jmeno and jezdec.prijmeni == prijmeni and jezdec.trida == trida for jezdec in jezdci):
            return jsonify({'error': 'Tento žák je již zaregistrovaný.'}), 400

        if not plavec:
            return jsonify({'error': 'Musíte označit, zda jste plavec.'}), 400

        jezdci.append(Jezdec(uzivatelske_jmeno, heslo, jmeno, prijmeni, trida, plavec))
        session['uzivatelske_jmeno'] = uzivatelske_jmeno
        return jsonify({'success': 'Registrace proběhla úspěšně.'})


@app.route('/prihlaseni', methods=['GET', 'POST'])
def prihlaseni():
    if request.method == 'GET':
        return render_template('prihlaseni.html'), 200

    if request.method == 'POST':
        data = request.json
        uzivatelske_jmeno = data.get("uzivatelske_jmeno")
        heslo = data.get("heslo")

    if any(jezdec.uzivatelske_jmeno == uzivatelske_jmeno and jezdec.heslo == heslo for jezdec in jezdci):
        session['uzivatelske_jmeno'] = uzivatelske_jmeno
        return jsonify({'success': 'Přihlášení proběhlo úspěšně.'})

    return jsonify({'error': 'Neplatné uživatelské jméno nebo heslo.'}), 400


@app.route('/odhlaseni', methods=['GET'])
def odhlaseni():
    session.pop('uzivatelske_jmeno', None)
    session.pop('filtr_jmena', None)
    session.pop('filtr_prijmeni', None)
    session.pop('filtr_tridy', None)
    session.pop('filtr_jmena-lodky', None)
    session.pop('filtr_prijmeni-lodky', None)
    session.pop('filtr_tridy-lodky', None)
    return redirect('/'), 302


@app.route('/jezdec', methods=['GET'])
def jezdec():
    if 'uzivatelske_jmeno' not in session:
        return redirect('/prihlaseni'), 302

    jezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == session['uzivatelske_jmeno']), None)

    if jezdec is None:
        return redirect('/prihlaseni'), 302

    pozvanky = filtrace_pozvanek(jezdec.pozvanky)

    spolujezdec = None
    if jezdec.spolujezdec:
        spolujezdec = jezdec.spolujezdec
        spolujezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == spolujezdec), None)
        spolujezdec = {'uzivatelske_jmeno': spolujezdec.uzivatelske_jmeno, 'jmeno': spolujezdec.jmeno,
                       'prijmeni': spolujezdec.prijmeni, 'trida': spolujezdec.trida}

    return render_template('jezdec.html', spolujezdec=spolujezdec, pozvanky=pozvanky), 200


@app.route('/smazat-jezdce', methods=['GET'])
def smazat_jezdce():
    if 'uzivatelske_jmeno' not in session:
        return redirect('/prihlaseni'), 302

    jezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == session['uzivatelske_jmeno']), None)

    if jezdec is None:
        return redirect('/prihlaseni'), 302

    return jezdec.smazat_jezdce()


def filtrace_pozvanek(pozvanky):
    vysledek = []
    for pozvanka in pozvanky:
        jezdec_pozvanka = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == pozvanka), None)
        vysledek.append({'uzivatelske_jmeno': jezdec_pozvanka.uzivatelske_jmeno, 'jmeno': jezdec_pozvanka.jmeno,
                         'prijmeni': jezdec_pozvanka.prijmeni, 'trida': jezdec_pozvanka.trida})
    return vysledek


@app.route('/odstranit-spolujezdce', methods=['POST'])
def odstranit_spolujezdce():
    if 'uzivatelske_jmeno' not in session:
        return redirect('/prihlaseni'), 302

    jezdec_sam = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == session['uzivatelske_jmeno']), None)
    jezdec_spolujezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == jezdec_sam.spolujezdec), None)
    jezdec_spolujezdec.spolujezdec = None
    jezdec_sam.spolujezdec = None

    odebrat_lodku(jezdec_sam.uzivatelske_jmeno)

    return redirect('/jezdec'), 302


@app.route('/poslat-pozvanku', methods=['POST'])
def poslat_pozvanku():
    if 'uzivatelske_jmeno' not in session:
        return redirect('/prihlaseni'), 302

    jezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == session['uzivatelske_jmeno']), None)

    if jezdec is None:
        return redirect('/prihlaseni'), 302

    data = request.json
    spolujezdec = data.get("spolujezdec")

    return jezdec.poslat_pozvanku(spolujezdec)


@app.route('/prijmout-pozvanku', methods=['POST'])
def prijmout_pozvanku():
    if 'uzivatelske_jmeno' not in session:
        return redirect('/prihlaseni'), 302

    jezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == session['uzivatelske_jmeno']), None)

    if jezdec is None:
        return redirect('/prihlaseni'), 302

    data = request.json
    odesilatel = data.get("odesilatel")

    return jezdec.prijmout_pozvanku(odesilatel)


@app.route('/odmitnout-pozvanku', methods=['POST'])
def odmitnout_pozvanku():
    if 'uzivatelske_jmeno' not in session:
        return redirect('/prihlaseni'), 302

    jezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == session['uzivatelske_jmeno']), None)

    if jezdec is None:
        return redirect('/prihlaseni'), 302

    data = request.json
    odesilatel = data.get("odesilatel")

    return jezdec.odmitnout_pozvanku(odesilatel)


@app.route('/seznam-jezdcu', methods=['GET', 'POST'])
def seznam_jezdcu():
    if 'uzivatelske_jmeno' not in session:
        return redirect('/prihlaseni'), 302

    jezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == session['uzivatelske_jmeno']), None)

    if jezdec is None:
        return redirect('/prihlaseni'), 302

    filtr_jmena = None
    filtr_prijmeni = None
    filtr_tridy = None

    if request.method == 'GET':
        filtr_jmena = session.get('filtr_jmena', '')
        filtr_prijmeni = session.get('filtr_prijmeni', '')
        filtr_tridy = session.get('filtr_tridy', '')

    if request.method == 'POST':
        filtr_jmena = request.form.get('jmeno', '')
        filtr_prijmeni = request.form.get('prijmeni', '')
        filtr_tridy = request.form.get('trida', '')

        session['filtr_jmena'] = filtr_jmena
        session['filtr_prijmeni'] = filtr_prijmeni
        session['filtr_tridy'] = filtr_tridy

    filtrovani_jezdci = filtrovat_jezdce(filtr_jmena, filtr_prijmeni, filtr_tridy)

    filtrovani_jezdci.sort(key=lambda jezdec: (jezdec['trida'], jezdec['prijmeni'], jezdec['jmeno']))

    return render_template('seznam_jezdcu.html', jezdci=filtrovani_jezdci,
                           tridy=tridy), 200


def filtrace(filtr, jezdec):
    index_filtr = 0
    index_jezdec = 0

    while index_filtr < len(filtr) and index_jezdec < len(jezdec):
        if filtr[index_filtr].lower() == jezdec[index_jezdec].lower():
            index_filtr += 1
        index_jezdec += 1

    return index_filtr == len(filtr)


def filtrovat_jezdce(jmena, prijmeni, tridy):
    filtrovani_jezdci = jezdci

    if jmena:
        filtrovani_jezdci = [jezdec for jezdec in filtrovani_jezdci if filtrace(jmena, jezdec.jmeno)]

    if prijmeni:
        filtrovani_jezdci = [jezdec for jezdec in filtrovani_jezdci if filtrace(prijmeni, jezdec.prijmeni)]

    if tridy and tridy != '---':
        filtrovani_jezdci = [jezdec for jezdec in filtrovani_jezdci if jezdec.trida == tridy]

    vysledek = []

    for jezdec in filtrovani_jezdci:
        vysledek.append({'jmeno': jezdec.jmeno, 'prijmeni': jezdec.prijmeni, 'trida': jezdec.trida})

    return vysledek


@app.route('/seznam-lodek', methods=['GET', 'POST'])
def seznam_lodek():
    if 'uzivatelske_jmeno' not in session:
        return redirect('/prihlaseni'), 302

    jezdec = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == session['uzivatelske_jmeno']), None)

    if jezdec is None:
        return redirect('/prihlaseni'), 302

    filtr_jmena = None
    filtr_prijmeni = None
    filtr_tridy = None

    if request.method == 'GET':
        filtr_jmena = session.get('filtr_jmena-lodky', '')
        filtr_prijmeni = session.get('filtr_prijmeni-lodky', '')
        filtr_tridy = session.get('filtr_tridy-lodky', '')

    if request.method == 'POST':
        filtr_jmena = request.form.get('jmeno', '')
        filtr_prijmeni = request.form.get('prijmeni', '')
        filtr_tridy = request.form.get('trida', '')

        session['filtr_jmena-lodky'] = filtr_jmena
        session['filtr_prijmeni-lodky'] = filtr_prijmeni
        session['filtr_tridy-lodky'] = filtr_tridy

    filtrovane_lodky = filtrovat_lodky(filtr_jmena, filtr_prijmeni, filtr_tridy)

    return render_template('seznam_lodek.html', lodky=filtrovane_lodky, tridy=tridy), 200


def filtrovat_lodky(jmena, prijmeni, trida):
    filtrovane_lodky = []

    for lodka in lodky:
        jezdec1 = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == lodka.jezdci[0]), None)
        jezdec2 = next((jezdec for jezdec in jezdci if jezdec.uzivatelske_jmeno == lodka.jezdci[1]), None)
        if jezdec1 and jezdec2:
            if ((not jmena or filtrace(jmena, jezdec1.jmeno)) and (
                    not prijmeni and filtrace(prijmeni, jezdec1.prijmeni)) and (
                        trida == '---' or trida == jezdec1.trida)) or (
                    (not jmena or filtrace(jmena, jezdec2.jmeno)) and (not
                                                                       prijmeni or filtrace(prijmeni,
                                                                                            jezdec2.prijmeni)) and (
                            trida == '---' or trida == jezdec2.trida)):
                filtrovane_lodky.append(Lodka([f'{jezdec1.jmeno} {jezdec1.prijmeni}, {jezdec1.trida}',
                                               f'{jezdec2.jmeno} {jezdec2.prijmeni}, {jezdec2.trida}']))

    return filtrovane_lodky


if __name__ == '__main__':
    app.run(host='localhost', port=5050)
