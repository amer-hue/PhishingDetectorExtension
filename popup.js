document.getElementById('checkButton').addEventListener('click', () => {
    const emailContent = document.getElementById('emailContent').value.trim();
    const resultDiv = document.getElementById('result');

    if (!emailContent) {
        alert("Please paste an email to analyze.");
        return;
    }

    // Clear previous result and styling
    resultDiv.textContent = '';
    resultDiv.className = '';

    // Send the email content to the Flask API for phishing detection
    fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailContent })
    })
        .then(response => response.json())  // Parse JSON response
        .then(data => {
            // Display the result with appropriate styling
            if (data.result === "Phishing") {
                resultDiv.textContent = "Result: Phishing";
                resultDiv.classList.add('result-phishing');
            } else {
                resultDiv.textContent = "Result: Legitimate";
                resultDiv.classList.add('result-legitimate');
            }
        })
        .catch(error => {
            console.error("Error contacting Flask API:", error);
            resultDiv.textContent = "Error: Unable to detect phishing.";
            resultDiv.classList.add('result-phishing'); // Display in red
        });
});