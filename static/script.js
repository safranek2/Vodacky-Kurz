function validateForm(form) {
    let nick = form.querySelector("#fnick").value;
    let jePlavec = form.querySelector("#rplavec").checked;
    let kanoeKamarad = form.querySelector("#fspolujezdec").value;

    if (nick.length < 2 || nick.length > 20 || !/^[a-zA-Z0-9]+$/.test(nick)) {
        alert("Přezdívka musí obsahovat 2 až 20 znaků a smí obsahovat pouze písmena a čísla.");
        return false;
    } else if (!jePlavec) {
        alert("Musíte označit, zda jste plavec.");
        return false;
    } else if (kanoeKamarad && (kanoeKamarad.length < 2 || kanoeKamarad.length > 20 || !/^[a-zA-Z0-9]+$/.test(kanoeKamarad))) {
        alert("Přezdívka pro spolujezdce může obsahovat pouze 2 až 20 znaků a smí obsahovat pouze písmena a čísla.");
        return false;
    }

    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/check-nickname?nick=" + nick, false);
    xhr.send();

    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText);
        if (response.exists) {
            alert("Tento nick již existuje.");
            return false;
        }
    }

    let xhr2 = new XMLHttpRequest();
    xhr2.open("GET", "/api/check-nickname?nick=" + kanoeKamarad, false);
    xhr2.send();

    if (kanoeKamarad) {
        if (xhr2.status === 200) {
            let response = JSON.parse(xhr2.responseText);
            if (!response.exists) {
                alert("Tento spolujezdec neexistuje.");
                return false;
            }
        }
    }

    return true;
}
