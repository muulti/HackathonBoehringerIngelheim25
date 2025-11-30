document.addEventListener("DOMContentLoaded", () => {
    // 1. Cargar pacientes desde un endpoint Flask
        async function loadPatients() {
            const res = await fetch("/api/pacientes");
            const data = await res.json();

            const list = document.getElementById("patient-list");
            list.innerHTML = ""; // limpiar por si recargamos

            data.forEach(p => {
                const block = document.createElement("div");
                block.className = "form-container";  // usa tus estilos de caja
                block.style.cursor = "pointer";

                block.innerHTML = `
                    <h3>Paciente #${p.id}</h3>
                    <p class="subtitle">Edad: ${p.age} — Sexo: ${p.sex}</p>
                `;

                block.onclick = () => openPatient(p.id);
                list.appendChild(block);
            });
        }

        // 2. Al pulsar un paciente → navegar al detalle
        function openPatient(id) {
            window.location.href = `/paciente/${id}`;
        }

        loadPatients();
});