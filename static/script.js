async function validaceRegistrace(form) {
    event.preventDefault();

    let uzivatelske_jmeno = form.querySelector("#fuzivatelske_jmeno").value;
    let heslo = form.querySelector("#fheslo").value;
    let jmeno = form.querySelector("#fjmeno").value;
    let prijmeni = form.querySelector("#fprijmeni").value;
    let trida = form.querySelector("#strida").value;
    let plavec = document.getElementById("rplavec").checked;


    if (await upozorneni('/registrace', {
        uzivatelske_jmeno,
        heslo,
        jmeno,
        prijmeni,
        trida,
        plavec
    })) {
        location.replace("/jezdec")
        form.submit()
    } else {
        return false;
    }
}

async function validacePrihlaseni(form) {
    event.preventDefault();

    let uzivatelske_jmeno = form.querySelector("#fuzivatelske_jmeno").value;
    let heslo = form.querySelector("#fheslo").value;

    if (await upozorneni('/prihlaseni', {
        uzivatelske_jmeno,
        heslo
    })) {
        location.replace("/jezdec")
        form.submit()
    } else {
        return false;
    }
}

async function validacePoslaniPozvanky(form) {
    event.preventDefault();

    let spolujezdec = form.querySelector("#fspolujezdec").value;

    if (await upozorneni('/poslat-pozvanku', {
        spolujezdec
    })) {
        location.replace("/jezdec")
        form.submit()
    } else {
        return false;
    }
}

async function validacePrijmutiPozvanky(odesilatel) {
    event.preventDefault();

    await upozorneni('/prijmout-pozvanku', {
        odesilatel
    })
    location.replace("/jezdec")
}

async function validaceOdmitnutiPozvanky(odesilatel) {
    event.preventDefault();

    if (await upozorneni('/odmitnout-pozvanku', {
        odesilatel
    })) {
        location.replace("/jezdec")
    } else {
        return false;
    }
}

function potvrditSmazani(){
    event.preventDefault();
    if(confirm('Určitě chcete smazat účet?'))
        location.replace("/smazat-jezdce")
}


async function upozorneni(odkaz, data = {}) {
    try {
        let odpoved = await fetch(odkaz, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!odpoved.ok) {
            let dataOdpovedi = await odpoved.json();
            alert(dataOdpovedi.error);
            return false;
        }

        let dataOdpovedi = await odpoved.json();
        alert(dataOdpovedi.success);
        return true;
    } catch (error) {
        alert('Chyba při komunikaci se serverem.');
        return false;
    }
}
