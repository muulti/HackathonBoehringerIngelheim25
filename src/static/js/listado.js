
let allPatients = [];

async function loadPatients() {
    try {
        const response = await fetch("/api/pacientes");
        allPatients = await response.json();

        document.getElementById('loading').style.display = 'none';
        document.getElementById('patient-list').style.display = 'block';

        renderPatients(allPatients);
    } catch (error) {
        document.getElementById('loading').innerHTML = `
            <h3>❌ Error al cargar pacientes</h3>
            <p>${error.message}</p>
        `;
    }
}

function renderPatients(patients) {
    const list = document.getElementById("patient-list");

    if (patients.length === 0) {
        list.style.display = 'none';
        document.getElementById('no-results').style.display = 'block';
        return;
    }

    list.style.display = 'block';
    document.getElementById('no-results').style.display = 'none';
    list.innerHTML = "";

    patients.forEach(p => {
        const card = document.createElement("div");
        card.className = "patient-card";

        card.innerHTML = `
            <h3>👤 Paciente #${p.id}</h3>
            <div class="patient-stats">
                <div class="stat-item">
                    <span class="stat-icon">🎂</span>
                    <span><strong>Edad:</strong> ${p.edad} años</span>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">${p.sexo === 'H' ? '👨' : '👩'}</span>
                    <span><strong>Sexo:</strong> ${p.sexo === 'H' ? 'Masculino' : 'Femenino'}</span>
                </div>
            </div>
        `;

        card.addEventListener("click", () => {
            window.location.href = `/paciente/${p.id}`;
        });

        list.appendChild(card);
    });
}

// Búsqueda en tiempo real
document.getElementById('search-input').addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();

    const filtered = allPatients.filter(p => {
        const id = p.id.toString();
        const edad = p.edad.toString();
        const sexo = p.sexo === 'H' ? 'masculino hombre h' : 'femenino mujer f';

        return id.includes(searchTerm) ||
               edad.includes(searchTerm) ||
               sexo.includes(searchTerm);
    });

    renderPatients(filtered);
});

// Cargar pacientes al iniciar
loadPatients();