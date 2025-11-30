// Estado de la aplicación
let currentStep = 0;
const totalSteps = 4;

// Objeto para almacenar los datos del formulario
const formData = {
    id: '',
    age: '',
    sex: '',
    smoking_level: '0',
    passive_smoker: '0',
    occupation_hazard: '0',
    genetic_risk: '0',
    chronic_lung_disease: '0',
    air_pollution: '0',
    alcohol_use: '0',
    obesity: '0',
    chest_pain: '0',
    shortness_of_breath: '0',
    wheezing: '0',
    hemoptysis_level: '0',
    fatigue: '0',
    swallowing_difficulty: '0',
    clubbing_nails: '0',
    weight_loss: ''
};

// Elementos del DOM
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const submitBtn = document.getElementById('submitBtn');
const resultContainer = document.getElementById('resultContainer');
const newEvalBtn = document.getElementById('newEvalBtn');
const downloadBtn = document.getElementById('downloadBtn');
const sendBtn = document.getElementById('send-btn');

// Inicializar event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Configurar todos los inputs de tipo range
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        input.addEventListener('input', updateRangeValue);
        updateRangeValue.call(input);
    });

    /*// Configurar toggle buttons
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    toggleButtons.forEach(button => {
        button.addEventListener('click', handleToggleButton);
    });*/

    // Selección de botones
    const toggleButtons = document.querySelectorAll(".toggle-btn");

    toggleButtons.forEach(button => {
        button.addEventListener("click", handleToggleButton);
    });

    function handleToggleButton(e) {
        const button = e.currentTarget;
        const field = button.dataset.field;
        const value = button.dataset.value;

        // Guarda el valor en formData
        formData[field] = value;
        console.log("Actualizado:", field, "=", value);

        // Actualiza solo el estilo visual
        const siblings = button.parentElement.querySelectorAll(".toggle-btn");
        siblings.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");
    }


    // Configurar navigation buttons
    prevBtn.addEventListener('click', previousStep);
    nextBtn.addEventListener('click', nextStep);
    submitBtn.addEventListener('click', calculateRisk);
    newEvalBtn.addEventListener('click', resetForm);
    downloadBtn.addEventListener('click', downloadData);
    sendBtn.addEventListener('click', enviar_form);
    // Cargar datos guardados en inputs
    loadFormData();
});

async function enviar_form() {
    const data = formData
    console.log("FORM DATA ANTES DE ENVIAR:", formData);
    const response = await fetch("/procesar-paciente", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    console.log("mandando:");
    const result = await response.json();
    msg = "Correctamente integrado"
    sendBtn.textContent = msg;
    console.log("Respuesta del backend:", result);
}
// Actualizar el valor mostrado de los range inputs
function updateRangeValue() {
    const valueSpan = this.parentElement.querySelector('.range-value');
    if (valueSpan) {
        valueSpan.textContent = this.value;
    }
    document.getElementById("patient-id").addEventListener("input", function () {
        formData[this.id] = this.value;
    });
}

// Manejar clicks en toggle buttons
/*function handleToggleButton(e) {
    const button = e.currentTarget;
    const field = button.dataset.field;
    const value = button.dataset.value;
    
    // Remover active de todos los botones del mismo grupo
    const group = button.parentElement;
    group.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Activar el botón clickeado
    button.classList.add('active');
    
    // Guardar el valor
    formData[field] = value;
}*/

// Cargar datos del formulario en los inputs
function loadFormData() {
    Object.keys(formData).forEach(key => {
        const input = document.getElementById(key);
        if (input) {
            input.value = formData[key];
            if (input.type === 'range') {
                updateRangeValue.call(input);
            }
        }
    });
    
    // Actualizar toggle buttons
    document.querySelectorAll('.toggle-btn').forEach(button => {
        const field = button.dataset.field;
        const value = button.dataset.value;
        if (formData[field] === value) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// Guardar datos del formulario
function saveFormData() {
    Object.keys(formData).forEach(key => {
        const input = document.getElementById(key);
        if (input) {
            formData[key] = input.value;
        }
    });
}

// Navegar al paso anterior
function previousStep() {
    if (currentStep > 0) {
        saveFormData();
        currentStep--;
        updateStepDisplay();
    }
}

// Navegar al siguiente paso
function nextStep() {
    saveFormData();
    
    if (!validateCurrentStep()) {
        return;
    }
    
    if (currentStep < totalSteps - 1) {
        currentStep++;
        updateStepDisplay();
    }
}

// Validar el paso actual
function validateCurrentStep() {
    if (currentStep === 0) {
        const age = document.getElementById('age').value;
        const sex = formData.sex;
        
        if (!age || age < 1 || age > 120) {
            alert('Por favor, introduce una edad válida');
            return false;
        }
        if (!sex) {
            alert('Por favor, selecciona el sexo');
            return false;
        }
    }
    return true;
}

// Actualizar la visualización del paso actual
function updateStepDisplay() {
    // Ocultar todos los pasos
    const steps = document.querySelectorAll('.form-step');
    steps.forEach(step => step.classList.remove('active'));
    
    // Mostrar el paso actual
    const currentStepElement = document.getElementById(`step${currentStep}`);
    if (currentStepElement) {
        currentStepElement.classList.add('active');
    }
    
    // Actualizar indicadores de progreso
    const stepIndicators = document.querySelectorAll('.step');
    stepIndicators.forEach((indicator, index) => {
        indicator.classList.remove('active', 'completed');
        if (index === currentStep) {
            indicator.classList.add('active');
        } else if (index < currentStep) {
            indicator.classList.add('completed');
        }
    });
    
    // Actualizar botones de navegación
    prevBtn.style.display = currentStep > 0 ? 'block' : 'none';
    nextBtn.style.display = currentStep < totalSteps - 1 ? 'block' : 'none';
    submitBtn.style.display = currentStep === totalSteps - 1 ? 'block' : 'none';
}

// Calcular el riesgo
function calculateRisk() {
    saveFormData();
    
    if (!formData.age || !formData.sex) {
        alert('Por favor, completa todos los campos obligatorios');
        return;
    }
    
    // Algoritmo de cálculo de riesgo
    const age = parseInt(formData.age);
    const ageWeight = age > 50 ? 2 : 1;
    const smokingWeight = parseInt(formData.smoking_level) || 0;
    
    const symptomsAvg = (
        parseInt(formData.chest_pain || 0) +
        parseInt(formData.shortness_of_breath || 0) +
        parseInt(formData.clubbing_nails || 0)
    ) / 3;
    
    const chronicWeight = parseInt(formData.chronic_lung_disease) || 0;
    const geneticWeight = parseInt(formData.genetic_risk) || 0;
    const hemoptysisWeight = parseInt(formData.hemoptysis_level) || 0;
    
    const riskScore = (
        ageWeight * 5 +
        smokingWeight * 3 +
        symptomsAvg * 4 +
        chronicWeight * 8 +
        geneticWeight * 6 +
        hemoptysisWeight * 10
    );
    
    // Determinar nivel de riesgo
    let riskLevel, riskClass, recommendation, iconEmoji;
    console.log(riskScore);
    console.log(riskScore);
    console.log(riskScore);
    console.log(riskScore);
    console.log(riskScore);
    if (riskScore > 50) {
        riskLevel = 'ALTO';
        riskClass = 'high';
        recommendation = 'Se recomienda derivación urgente a Oncología para estudio avanzado';
        iconEmoji = '⚠️';
    } else if (riskScore > 30) {
        riskLevel = 'MEDIO';
        riskClass = 'medium';
        recommendation = 'Se recomienda realizar pruebas complementarias y seguimiento estrecho';
        iconEmoji = '⚡';
    } else {
        riskLevel = 'BAJO';
        riskClass = 'low';
        recommendation = 'Riesgo bajo. Continuar con seguimiento habitual';
        iconEmoji = '✓';
    }
    
    // Guardar evaluación
    savePatientEvaluation({
        ...formData,
        riskLevel: riskClass,
        riskScore: riskScore
    });
    
    // Mostrar resultados
    displayResults(riskLevel, riskClass, recommendation, iconEmoji);
}

// Guardar evaluación del paciente
function savePatientEvaluation(evaluation) {
    // Obtener datos existentes
    let patientsData = JSON.parse(localStorage.getItem('patientsData') || '[]');
    
    // Añadir nueva evaluación
    patientsData.push({
        ...evaluation,
        timestamp: new Date().toISOString(),
        patient_id: patientsData.length + 1
    });
    
    // Guardar en localStorage
    localStorage.setItem('patientsData', JSON.stringify(patientsData));
}

// Mostrar los resultados
function displayResults(riskLevel, riskClass, recommendation, iconEmoji) {
    // Ocultar formulario
    document.querySelector('.form-container').style.display = 'none';
    document.querySelector('.progress-container').style.display = 'none';
    
    // Configurar y mostrar resultados
    const resultIcon = document.getElementById('resultIcon');
    resultIcon.className = `result-icon ${riskClass}`;
    resultIcon.textContent = iconEmoji;
    
    const resultLevelElement = document.getElementById('resultLevel');
    resultLevelElement.className = `result-level ${riskClass}`;
    resultLevelElement.textContent = `Riesgo ${riskLevel}`;
    
    const resultRecommendation = document.getElementById('resultRecommendation');
    resultRecommendation.innerHTML = `
        <h3>Recomendación:</h3>
        <p>${recommendation}</p>
    `;
    
    resultContainer.style.display = 'block';
    
    // Scroll al principio
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Resetear el formulario
function resetForm() {
    // Resetear datos
    Object.keys(formData).forEach(key => {
        if (key === 'age' || key === 'sex' || key === 'weight_loss') {
            formData[key] = '';
        } else {
            formData[key] = '0';
        }
    });
    
    // Resetear paso
    currentStep = 0;
    
    // Cargar datos reseteados
    loadFormData();
    
    // Mostrar formulario
    document.querySelector('.form-container').style.display = 'block';
    document.querySelector('.progress-container').style.display = 'block';
    resultContainer.style.display = 'none';
    
    // Actualizar visualización
    updateStepDisplay();
    
    // Scroll al principio
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Descargar datos en formato JSON
function downloadData() {
    const dataToDownload = {
        ...formData,
        timestamp: new Date().toISOString(),
        patient_id: Math.floor(Math.random() * 10000) + 1
    };
    
    const jsonString = JSON.stringify(dataToDownload, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `evaluacion-riesgo-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}


// Inicializar la visualización
updateStepDisplay();