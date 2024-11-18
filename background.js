// background.js

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "sendToAPI") {
        // Send the email content to the Flask API for phishing detection
        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: message.emailContent })
        })
            .then(response => response.json())  // Parse JSON response
            .then(data => {
                // Send the result back to the content or popup script
                sendResponse({ result: data.result });
            })
            .catch(error => {
                console.error("Error contacting Flask API:", error);
                sendResponse({ result: "Error: Unable to detect phishing." });
            });
        return true;  // Keep the message channel open for async response
    }
});