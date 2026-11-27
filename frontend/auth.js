const form = document.getElementById("auth-form");
const message = document.getElementById("auth-message");
const submitButton = form.querySelector("[type='submit']");
const demoSection = document.getElementById("auth-demo");
const locationInput = document.getElementById("location");
const locationSearchButton = document.getElementById("location-search");
const locationResults = document.getElementById("location-results");
const locationStatus = document.getElementById("location-status");
let selectedLocation = null;
let locationSearchTimer = null;
let locationSearchController = null;

function showMessage(text) {
    message.textContent = text;
    message.hidden = !text;
}

function getErrorMessage(detail) {
    if (typeof detail === "string") return detail;
    return "Please check the details and try again.";
}

async function authenticate(endpoint, credentials) {
    showMessage("");
    submitButton.disabled = true;
    submitButton.textContent = "Connecting securely...";

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify(credentials)
        });
        const data = await response.json();

        if (!response.ok) {
            showMessage(getErrorMessage(data.detail));
            return;
        }

        window.location.assign("/");
    } catch {
        showMessage("The service is unavailable right now. Please try again shortly.");
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = form.dataset.submitLabel;
    }
}

form.addEventListener("submit", event => {
    event.preventDefault();
    const values = new FormData(form);
    const credentials = {
        mobile_number: values.get("mobile_number"),
        password: values.get("password")
    };

    if (form.dataset.authMode === "register") {
        if (!selectedLocation) {
            showMessage("Search for your location and select a verified result before creating an account.");
            locationInput.focus();
            return;
        }
        credentials.location = selectedLocation.name;
        credentials.latitude = selectedLocation.latitude;
        credentials.longitude = selectedLocation.longitude;
    }

    authenticate(`/api/auth/${form.dataset.authMode}`, credentials);
});

if (locationSearchButton) {
    locationInput.addEventListener("input", () => {
        selectedLocation = null;
        document.getElementById("location-latitude").value = "";
        document.getElementById("location-longitude").value = "";
        if (locationSearchTimer) clearTimeout(locationSearchTimer);
        if (locationSearchController) locationSearchController.abort();
        locationSearchButton.disabled = false;
        locationResults.replaceChildren();
        locationResults.hidden = true;
        locationInput.setAttribute("aria-expanded", "false");
        if (locationInput.value.trim().length >= 3) {
            locationStatus.textContent = "Looking for matching places...";
            locationSearchTimer = setTimeout(searchLocations, 1200);
        } else {
            locationStatus.textContent = "Enter at least 3 characters to find a real place.";
        }
    });

    locationSearchButton.addEventListener("click", () => {
        if (locationSearchTimer) clearTimeout(locationSearchTimer);
        searchLocations();
    });

    async function searchLocations() {
        const query = locationInput.value.trim();
        if (query.length < 3) {
            locationStatus.textContent = "Enter at least 3 characters to search.";
            return;
        }

        const controller = new AbortController();
        locationSearchController = controller;
        locationSearchButton.disabled = true;
        locationStatus.textContent = "Searching verified map places...";
        locationResults.replaceChildren();
        locationResults.hidden = true;
        try {
            const response = await fetch(`/api/auth/locations/search?q=${encodeURIComponent(query)}`, {
                signal: controller.signal
            });
            const data = await response.json();
            if (!response.ok) throw new Error(getErrorMessage(data.detail));
            if (!data.results.length) {
                locationStatus.textContent = "No matching place found. Try adding a district or country.";
                return;
            }

            data.results.forEach(place => {
                const option = document.createElement("button");
                option.type = "button";
                option.className = "location-option";
                option.setAttribute("role", "option");
                option.textContent = place.name;
                option.addEventListener("click", () => {
                    selectedLocation = place;
                    locationInput.value = place.name;
                    document.getElementById("location-latitude").value = place.latitude;
                    document.getElementById("location-longitude").value = place.longitude;
                    locationResults.replaceChildren();
                    locationResults.hidden = true;
                    locationInput.setAttribute("aria-expanded", "false");
                    locationStatus.textContent = `Selected: ${place.latitude.toFixed(4)}, ${place.longitude.toFixed(4)}`;
                    showMessage("");
                });
                locationResults.appendChild(option);
            });
            locationResults.hidden = false;
            locationInput.setAttribute("aria-expanded", "true");
            locationStatus.textContent = "Select the correct place from the results.";
        } catch (error) {
            if (error.name !== "AbortError") {
                locationStatus.textContent = error.message || "Location search is temporarily unavailable.";
            }
        } finally {
            if (locationSearchController === controller) {
                locationSearchController = null;
                locationSearchButton.disabled = false;
            }
        }
    }
}

const demoButton = document.getElementById("demo-login");
if (demoButton) {
    demoButton.addEventListener("click", () => {
        authenticate("/api/auth/login", {
            mobile_number: demoButton.dataset.mobile,
            password: demoButton.dataset.password
        });
    });

    fetch("/api/auth/demo-credentials", { credentials: "same-origin" })
        .then(response => response.ok ? response.json() : null)
        .then(credentials => {
            if (!credentials) return;
            document.getElementById("demo-mobile").textContent = credentials.mobile_number;
            document.getElementById("demo-password").textContent = credentials.password;
            demoButton.dataset.mobile = credentials.mobile_number;
            demoButton.dataset.password = credentials.password;
            demoSection.hidden = false;
        })
        .catch(() => { });
}