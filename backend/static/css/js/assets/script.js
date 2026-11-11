
const form = document.getElementById("simulationForm");
const resultsContent = document.getElementById("resultsContent");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const button = form.querySelector(".simulate-button");
    const originalText = button.innerHTML;

    const data = {
        debit: Number(document.getElementById("debit").value),
        ajout: Number(document.getElementById("ajout").value),
        concentration: Number(document.getElementById("concentration").value),
        temperature: Number(document.getElementById("temperature").value)
    };

    button.disabled = true;
    button.innerHTML = "Calculating...";

    try {
        const response = await fetch("/calcul", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Calculation error");
        }

        displayResults(result);

    } catch (error) {
        resultsContent.innerHTML = `
            <div class="error-message">
                <h3>Simulation error</h3>
                <p>${escapeHTML(error.message)}</p>
            </div>
        `;

    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
});


function displayResults(result) {

    const labels = {
        debit_filtration: "Mass flow after filtration",
        debit_melange: "Mass flow after mixing",
        concentration_melange: "Concentration after mixing",
        puissance_chauffage: "Heating power",
        debit_vapeur: "Evaporated water flow",
        debit_final: "Final juice flow",
        puissance_evaporation: "Evaporation power",
        puissance_refroidissement: "Cooling power",
        ecart_bilan: "Global mass balance difference"
    };

    const units = {
        debit_filtration: "kg/h",
        debit_melange: "kg/h",
        concentration_melange: "%",
        puissance_chauffage: "kW",
        debit_vapeur: "kg/h",
        debit_final: "kg/h",
        puissance_evaporation: "kW",
        puissance_refroidissement: "kW",
        ecart_bilan: "kg/h"
    };

    let html = `
        <div class="result-grid">
    `;

    for (const key in labels) {

        if (result[key] !== undefined) {

            html += `
                <div class="result-item">
                    <span>${labels[key]}</span>
                    <strong>
                        ${result[key]} 
                        <small>${units[key]}</small>
                    </strong>
                </div>
            `;
        }
    }

    html += `
        </div>

        <div class="success-message">
            <span>✓</span>
            Simulation completed successfully.
        </div>
    `;

    resultsContent.innerHTML = html;

    const status = document.querySelector(".result-status");

    if (status) {
        status.textContent = "COMPLETED";
        status.style.background = "#e9f6ef";
        status.style.color = "#198754";
    }
}


function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[character];
    });
}


form.addEventListener("reset", function () {

    resultsContent.innerHTML = `
        <div class="empty-results">
            <div class="empty-icon">📊</div>
            <h3>No results yet</h3>
            <p>
                Enter your parameters and click
                "Run simulation" to generate results.
            </p>
        </div>
    `;

    const status = document.querySelector(".result-status");

    if (status) {
        status.textContent = "WAITING";
        status.removeAttribute("style");
    }

});
