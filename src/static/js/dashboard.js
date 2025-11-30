document.addEventListener('DOMContentLoaded', () => {
    updateKPI();
});

async function updateKPI() {
    try {
        const resp = await fetch('/api/total-pacientes');
        const data = await resp.json();

        const resp2 = await fetch('/api/medias-fases');
        const data2 = await resp2.json();

        //Coger los valores
        const totalElem = document.getElementById('totalPatients');
        const mediaTiempo = document.getElementById('avgTime');
        const riesgo = document.getElementById('highRisk');
        const tmpRed = document.getElementById('timeReduction');

        const mediaF1 = document.getElementById('fase1');
        const mediaF2 = document.getElementById('fase2');
        const mediaF3 = document.getElementById('fase3');
        const mediaF4 = document.getElementById('fase4');
        const mediaF5 = document.getElementById('fase5');
        const mediaF6 = document.getElementById('fase6');

        //Actualizarlos
        totalElem.textContent = data.totalPacientes;
        mediaTiempo.textContent = data.tiempoPromedio;
        riesgo.textContent = data.riesgo;
        tmpRed.textContent = data.extra;

        const clean = {};
        data2.forEach(obj => {
            const [key, value] = Object.entries(obj)[0];
            clean[key] = value;
        });
        console.log(clean.TiempoFase3);
        mediaF1.textContent = clean.TiempoFase1 + " días";
        mediaF2.textContent = clean.TiempoFase2 + " días";
        mediaF3.textContent = clean.TiempoFase3 + " días";
        mediaF4.textContent = clean.TiempoFase4 + " días";
        mediaF5.textContent = clean.TiempoFase5 + " días";
        mediaF6.textContent = clean.TiempoFase6 + " días";

console.log(clean.TiempoFase3);

    } catch (err) {
        console.error('Error cargando total de pacientes:', err);
    }
}