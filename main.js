// main.js

// This script can interact with the current webpage or listen for messages
// Example of sending a message to the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyzeEmailContent") {
        const emailContent = request.emailContent;

        // Here you can process or transform emailContent if necessary
        // For now, we will send it back to the background script
        chrome.runtime.sendMessage(
            { action: "sendToAPI", emailContent },
            (response) => {
                sendResponse(response);
            }
        );
    }
    return true; // Keep the message channel open for async response
});