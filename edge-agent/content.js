(function() {
  'use strict';

  console.log("✅ [TacitAgent v18] Script Loaded. Initializing...");

  const API_ENDPOINT_PREDICT = "http://127.0.0.1:8000/predict";
  const API_ENDPOINT_FEEDBACK = "http://127.0.0.1:8000/feedback";

  const SELECTORS = {
    mainPane: '[role="main"]',
    detailedView: {
      subject: 'h2.hP',
      sender: 'span.gD[email]'
    },
  };

  let mentorBar = null;

  function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      #mentor-bar { position: fixed; bottom: -100px; left: 50%; transform: translateX(-50%); background-color: #1e293b; color: #f1f5f9; padding: 12px 20px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 8px 30px rgba(0,0,0,0.25); display: flex; align-items: center; gap: 16px; font-family: sans-serif; z-index: 9999; transition: all 0.3s ease-in-out; }
      #mentor-bar.visible { bottom: 30px; }
      #mentor-bar-title { font-weight: 600; font-size: 14px; color: #94a3b8; }
      #mentor-bar-suggestion { font-weight: 700; font-size: 16px; color: #22d3ee; background-color: rgba(34, 211, 238, 0.1); padding: 4px 10px; border-radius: 8px; }
      .mentor-bar-button { background-color: #334155; color: #f1f5f9; border: none; padding: 8px 14px; border-radius: 8px; cursor: pointer; font-weight: 600; }
    `;
    document.head.appendChild(style);
  }

  function createMentorBar() {
    if (document.getElementById('mentor-bar')) return;
    mentorBar = document.createElement('div');
    mentorBar.id = 'mentor-bar';
    mentorBar.innerHTML = `
      <div id="mentor-bar-title">AI Coach:</div>
      <div id="mentor-bar-suggestion">...</div>
      <div id="mentor-bar-buttons">
          <button class="mentor-bar-button" id="mentor-accept">Accept</button>
          <button class="mentor-bar-button" id="mentor-reject">Reject</button>
      </div>
    `;
    document.body.appendChild(mentorBar);
    console.log("[TacitAgent] Mentor Bar created.");
  }

  async function sendFeedback(context, suggestion, feedbackType) {
    console.log(`[TacitAgent] --- Feedback process started for "${feedbackType}" ---`);
    if (!context || !suggestion) {
      console.error("[TacitAgent] 🔥 FEEDBACK ABORTED: Context or suggestion was missing when sending.");
      return;
    }

    const payload = { ...context, suggestion, feedback: feedbackType };
    console.log("[TacitAgent] 📦 Sending feedback payload:", payload);

    try {
      const response = await fetch(API_ENDPOINT_FEEDBACK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (response.ok) console.log(`[TacitAgent] 👍 Feedback sent successfully.`);
      else console.error("[TacitAgent] 🔥 Feedback server error:", response.status);
    } catch (error) {
      console.error("[TacitAgent] 🔥 Error sending feedback:", error);
    }
    hideMentorBar();
  }
  
  async function fetchPrediction(context) {
    try {
      const response = await fetch(API_ENDPOINT_PREDICT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(context) });
      if (response.ok) {
        const data = await response.json();
        showSuggestion(context, data.predicted_action);
      }
    } catch (error) {
        // Suppress console spam if server is down
    }
  }

  function showSuggestion(context, suggestion) {
    if (!mentorBar) return;
    
    // 🎯 THE FIX IS HERE: We re-create the buttons and their listeners
    // every time we show a suggestion, "locking in" the current context.
    const buttonContainer = mentorBar.querySelector('#mentor-bar-buttons');
    buttonContainer.innerHTML = `
      <button class="mentor-bar-button" id="mentor-accept">Accept</button>
      <button class="mentor-bar-button" id="mentor-reject">Reject</button>
    `;
    
    buttonContainer.querySelector('#mentor-accept').addEventListener('click', () => sendFeedback(context, suggestion, 'accepted'));
    buttonContainer.querySelector('#mentor-reject').addEventListener('click', () => sendFeedback(context, suggestion, 'rejected'));

    mentorBar.querySelector('#mentor-bar-suggestion').textContent = suggestion;
    mentorBar.classList.add('visible');
  }

  function hideMentorBar() {
    if (mentorBar) mentorBar.classList.remove('visible');
  }

  function initializeObserver() {
    const targetNode = document.querySelector(SELECTORS.mainPane);
    if (!targetNode) {
      setTimeout(initializeObserver, 2000);
      return;
    }
    
    let lastProcessedSubject = null;
    const observer = new MutationObserver(() => {
      const subjectEl = document.querySelector(SELECTORS.detailedView.subject);
      
      if (subjectEl) { // In detailed view
        if (subjectEl.innerText !== lastProcessedSubject) {
          const senderEl = document.querySelector(SELECTORS.detailedView.sender);
          if (senderEl) {
            lastProcessedSubject = subjectEl.innerText;
            const context = {
              subject: subjectEl.innerText,
              sender: senderEl.getAttribute('email'),
            };
            fetchPrediction(context);
          }
        }
      } else { // Not in detailed view
        if (lastProcessedSubject !== null) {
          lastProcessedSubject = null;
          hideMentorBar();
        }
      }
    });

    observer.observe(targetNode, { childList: true, subtree: true });
  }
  
  // --- Start the script ---
  injectStyles();
  createMentorBar();
  initializeObserver();

})();