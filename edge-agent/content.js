// content.js in edge-agent/ (v13 - Enhanced Error Logging)

console.log("✅ Tacit Agent v13 (Enhanced Logging) Loaded.");

const API_ENDPOINT = "http://127.0.0.1:8000/capture";

document.body.addEventListener('click', (event) => {
  const target = event.target;
  let context = null;
  let action = null;

  // --- Determine which view we are in ---
  const isDetailedView = !!document.querySelector('h2.hP');

  if (isDetailedView) {
    // --- LOGIC FOR DETAILED VIEW ---
    const clickableEl = target.closest('[role="menuitem"], [data-tooltip]');
    if (!clickableEl) return;

    let actionLabel = clickableEl.innerText || clickableEl.getAttribute('data-tooltip');
    
    if (actionLabel) {
      if (actionLabel.includes('Report spam')) action = 'Report spam';
      if (actionLabel.includes('Delete')) action = 'Delete';
      
      const subjectEl = document.querySelector('h2.hP');
      const senderEl = document.querySelector('span.gD[email]');
      if (subjectEl && senderEl) {
        context = {
          sender: senderEl.getAttribute('email'),
          subject: subjectEl.innerText,
        };
      }
    }
  } else {
    // --- LOGIC FOR INBOX VIEW ---
    const actionButton = target.closest('[data-tooltip="Archive"], [data-tooltip="Delete"]');
    if (actionButton) {
      action = actionButton.getAttribute('data-tooltip');
      const emailRow = target.closest('tr');
      if (emailRow) {
        const senderElement = emailRow.querySelector('[email]');
        // Using a general selector that finds the subject in read/unread emails
        const subjectElement = emailRow.querySelector('.bqe, .bog, span[data-legacy-thread-id]');
        
        if (senderElement && subjectElement) {
          context = {
            sender: senderElement.getAttribute('email'),
            subject: subjectElement.innerText,
          };
        }
      }
    }
  }

  // --- If we successfully found an action and a context, send the data ---
  if (action && context) {
    console.log(`✅ Success! Action: "${action}"`, context);
    const dataToSend = {
      ...context,
      capture_timestamp: new Date().toISOString(),
      user_decision: action,
    };
    sendData(dataToSend);
  }
}, true);


async function sendData(payload) {
  console.log("📦 Preparing to send data to backend...", payload);
  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (response.ok) {
      console.log("👍 Successfully sent data to backend.");
    } else {
      // Log server errors (e.g., 404 Not Found, 500 Internal Server Error)
      console.error("🔥 Server responded with an error:", response.status, await response.text());
    }
  } catch (error) {
    // Log network errors (e.g., server not running, CORS issue, URL wrong)
    console.error("🔥 A network error occurred:", error.message);
    console.error("👉 CHECK: Is your Python backend server running on the correct address?");
  }
}