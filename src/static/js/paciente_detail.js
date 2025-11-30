// Obtener ID del paciente de la URL
const pathParts = window.location.pathname.split('/');
const pacienteId = pathParts[pathParts.length - 1];

async function loadPatientJourney() {
    try {
        const response = await fetch(`/api/paciente/${pacienteId}/journey`);

        if (!response.ok) {
            throw new Error('Paciente no encontrado');
        }

        const data = await response.json();

        // Ocultar loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';

        // Datos del paciente
        document.getElementById('patient-id').textContent = data.paciente.id;
        document.getElementById('patient-edad').textContent = data.paciente.edad;
        document.getElementById('patient-sexo').textContent = data.paciente.sexo;
        document.getElementById('tiempo-total').textContent = data.resumen.tiempoTotal;
        document.getElementById('desplazamientos').textContent = data.resumen.desplazamientos;

        // Resumen
        document.getElementById('fases-completadas').textContent = data.resumen.fasesCompletadas;
        document.getElementById('fases-en-curso').textContent = data.resumen.fasesEnCurso;
        document.getElementById('fases-no-iniciadas').textContent = data.resumen.fasesNoIniciadas;

        // Alerta de cuello de botella
        if (data.resumen.faseMasLenta) {
            const alert = document.getElementById('bottleneck-alert');
            alert.style.display = 'block';
            alert.innerHTML = `
                <h4>⚠️ Cuello de Botella Identificado</h4>
                <p><strong>${data.resumen.faseMasLenta.nombre}</strong> es la fase más lenta con <strong>${data.resumen.faseMasLenta.dias} días</strong>.
                Esta fase requiere atención prioritaria para optimizar el journey del paciente.</p>
            `;
        }

        // Renderizar timeline de fases
        renderTimeline(data.fases, data.comparacion);

        // Renderizar eventos
        renderEvents(data.eventos);

    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
        document.getElementById('error-message').textContent = error.message;
    }
}

function renderTimeline(fases, comparacion) {
    const container = document.getElementById('timeline-fases');
    container.innerHTML = '';

    fases.forEach((fase, index) => {
        const comp = comparacion.find(c => c.fase === fase.numero);
        const esRetrasado = comp && comp.estado === 'retrasado';

        const item = document.createElement('div');
        item.className = 'timeline-item';

        const dot = document.createElement('div');
        dot.className = `timeline-dot ${fase.estado}`;
        item.appendChild(dot);

        const card = document.createElement('div');
        // Añadir clase según el estado
        card.className = `phase-card ${fase.estado} ${esRetrasado ? 'retrasado' : ''}`;

        let cardContent = `
            <div class="phase-header">
                <div>
                    <div class="phase-title">${fase.numero}. ${fase.nombre}</div>
                    <small style="color: #6b7280;">Eventos ${fase.eventoInicio} → ${fase.eventoFin}</small>
                </div>
                <div>
                    ${fase.dias !== null ? `
                        <div class="phase-days ${esRetrasado ? 'retrasado' : ''}">${fase.dias} días</div>
                    ` : `
                        <div style="color: #6b7280; font-style: italic;">
                            ${getEstadoLabel(fase.estado)}
                        </div>
                    `}
                </div>
            </div>
        `;

        if (fase.fechaInicio && fase.fechaFin) {
            cardContent += `
                <div class="phase-dates">
                    <div class="date-box">
                        <div class="date-label">📅 Inicio</div>
                        <div class="date-value">${formatDate(fase.fechaInicio)}</div>
                    </div>
                    <div class="date-box">
                        <div class="date-label">🏁 Fin</div>
                        <div class="date-value">${formatDate(fase.fechaFin)}</div>
                    </div>
                </div>
            `;
        } else if (fase.fechaInicio && fase.estado === 'en_curso') {
            // Mostrar solo fecha de inicio si está en curso
            cardContent += `
                <div class="phase-dates">
                    <div class="date-box">
                        <div class="date-label">📅 Inicio</div>
                        <div class="date-value">${formatDate(fase.fechaInicio)}</div>
                    </div>
                    <div class="date-box">
                        <div class="date-label">⏳</div>
                        <div class="date-value" style="color: #f59e0b; font-weight: bold;">En progreso...</div>
                    </div>
                </div>
            `;
        } else if (fase.estado === 'pendiente') {
            // Indicar que está pendiente por fases anteriores
            cardContent += `
                <div style="margin-top: 1rem; padding: 0.75rem; background-color: #fef3c7; border-radius: 0.5rem; border-left: 4px solid #f59e0b;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;">⏸️</span>
                        <span style="color: #92400e; font-size: 0.9rem;">
                            Pendiente - Esperando completar fases anteriores
                        </span>
                    </div>
                </div>
            `;
        }

        if (comp) {
            const signo = comp.diferencia > 0 ? '+' : '';
            cardContent += `
                <div class="comparison-badge ${comp.estado}">
                    ${comp.estado === 'retrasado' ? '⚠️' : '✓'}
                    ${signo}${comp.diferencia} días vs promedio (${comp.tiempoPromedio} días)
                    ${comp.porcentaje !== 0 ? ` | ${signo}${comp.porcentaje}%` : ''}
                </div>
            `;
        }

        card.innerHTML = cardContent;
        item.appendChild(card);
        container.appendChild(item);
    });
}

function getEstadoLabel(estado) {
    const labels = {
        'en_curso': '⏳ En curso',
        'no_iniciada': '⏸️ No iniciada',
        'pendiente': '🔒 Pendiente',
        'completada': '✅ Completada'
    };
    return labels[estado] || estado;
}

function renderEvents(eventos) {
    const container = document.getElementById('events-list');
    container.innerHTML = '';

    if (eventos.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #6b7280;">No hay eventos registrados</p>';
        return;
    }

    eventos.forEach(evento => {
        const item = document.createElement('div');
        item.className = 'event-item';
        item.innerHTML = `
            <div class="event-number">${evento.idEvento}</div>
            <div class="event-details">
                <div class="event-desc">${evento.descripcion}</div>
                <div class="event-date">📅 ${formatDate(evento.fecha)}</div>
            </div>
        `;
        container.appendChild(item);
    });
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Cargar datos al iniciar
loadPatientJourney();