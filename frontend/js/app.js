const form = document.getElementById("analyzeForm");

const button = document.getElementById("analyzeButton");

const statusElement = document.getElementById("status");

const resultsElement = document.getElementById("results");


function addListItems(elementId, items) {

    const list = document.getElementById(elementId);

    list.replaceChildren();

    if (items.length === 0) {

        const item = document.createElement("li");

        item.textContent =
            "No indicators detected by the current rules.";

        list.appendChild(item);

        return;
    }

    items.forEach(text => {

        const item = document.createElement("li");

        item.textContent = text;

        list.appendChild(item);
    });
}


function displayReport(data) {

    resultsElement.classList.remove("hidden");

    document.getElementById("riskScore").textContent =
        data.risk_score + "/100";

    document.getElementById("riskBadge").textContent =
        data.risk_level + " Risk";

    document.getElementById("prediction").textContent =
        data.prediction === 1
            ? "Potential Phishing"
            : "Predicted Legitimate";

    document.getElementById("modelName").textContent =
        "Model: " + data.model_name;

    document.getElementById("analysisMode").textContent =
        "Analysis: " + data.analysis_mode;

    document.getElementById("riskDescription").textContent =
        "Uncalibrated model-derived score. " +
        "A low score does not guarantee safety.";

    addListItems("indicators", data.indicators);

    addListItems(
        "recommendations",
        data.recommendations
    );

    const featuresElement =
        document.getElementById("features");

    featuresElement.replaceChildren();

    Object.entries(data.features).forEach(([name, value]) => {

        const container = document.createElement("div");

        container.className = "feature-item";

        const label = document.createElement("span");

        label.className = "feature-name";
        label.textContent = name;

        const featureValue = document.createElement("span");

        featureValue.className = "feature-value";
        featureValue.textContent = String(value);

        container.appendChild(label);
        container.appendChild(featureValue);

        featuresElement.appendChild(container);
    });

    resultsElement.scrollIntoView({
        behavior: "smooth"
    });
}


form.addEventListener("submit", async function(event) {

    event.preventDefault();

    const url = document.getElementById("urlInput").value;

    button.disabled = true;
    button.textContent = "Analyzing...";

    statusElement.textContent = "";

    resultsElement.classList.add("hidden");

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/analyze",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({ url: url })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Analysis failed."
            );
        }

        displayReport(data);

    } catch (error) {

        statusElement.textContent =
            "Error: " + error.message;

    } finally {

        button.disabled = false;

        button.textContent = "Analyze URL";
    }
});