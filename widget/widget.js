/**
 * DocQuery Embeddable Chat Widget
 * Drop-in chatbot for any documentation site.
 *
 * Usage:
 * <script
 *   src="https://docquery.vercel.app/widget.js"
 *   data-collection="vaultpay"
 *   data-api="https://docquery-api.railway.app"
 *   data-theme="light"
 *   data-position="bottom-right"
 * ></script>
 */
(function () {
  "use strict";

  var script = document.currentScript;
  var config = {
    collection: script?.getAttribute("data-collection") || "default",
    apiUrl: (script?.getAttribute("data-api") || "").replace(/\/$/, ""),
    theme: script?.getAttribute("data-theme") || "light",
    position: script?.getAttribute("data-position") || "bottom-right",
  };

  if (!config.apiUrl) {
    console.warn("DocQuery Widget: data-api attribute is required");
    return;
  }

  var sessionId = "dq_" + Math.random().toString(36).substring(2, 15);
  var isOpen = false;
  var messages = [];

  // Colors
  var colors =
    config.theme === "dark"
      ? { bg: "#1e293b", text: "#f1f5f9", input: "#334155", accent: "#818cf8", border: "#475569" }
      : { bg: "#ffffff", text: "#0f172a", input: "#f1f5f9", accent: "#6366f1", border: "#e2e8f0" };

  function createWidget() {
    // Floating button
    var btn = document.createElement("div");
    btn.id = "dq-chat-btn";
    btn.innerHTML = "💬";
    btn.style.cssText =
      "position:fixed;bottom:24px;" +
      (config.position === "bottom-left" ? "left" : "right") +
      ":24px;width:56px;height:56px;border-radius:50%;background:" +
      colors.accent +
      ";color:#fff;font-size:24px;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:10000;transition:transform 0.2s;";
    btn.addEventListener("mouseenter", function () { btn.style.transform = "scale(1.1)"; });
    btn.addEventListener("mouseleave", function () { btn.style.transform = "scale(1)"; });
    btn.addEventListener("click", toggleChat);

    // Chat panel
    var panel = document.createElement("div");
    panel.id = "dq-chat-panel";
    panel.style.cssText =
      "position:fixed;bottom:90px;" +
      (config.position === "bottom-left" ? "left" : "right") +
      ":24px;width:380px;max-height:520px;background:" +
      colors.bg +
      ";border:1px solid " +
      colors.border +
      ";border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,0.12);z-index:10001;display:none;flex-direction:column;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;";

    // Header
    var header = document.createElement("div");
    header.style.cssText =
      "padding:12px 16px;background:" +
      colors.accent +
      ";color:#fff;font-weight:600;font-size:14px;display:flex;align-items:center;justify-content:space-between;";
    header.innerHTML =
      '<span>DocQuery — Ask about docs</span><span style="cursor:pointer;font-size:18px;" id="dq-close">&times;</span>';

    // Messages area
    var messagesArea = document.createElement("div");
    messagesArea.id = "dq-messages";
    messagesArea.style.cssText =
      "flex:1;overflow-y:auto;padding:16px;max-height:360px;min-height:200px;";
    messagesArea.innerHTML =
      '<div style="font-size:13px;color:' +
      colors.text +
      ';opacity:0.6;text-align:center;padding:20px;">Ask a question about the documentation</div>';

    // Input area
    var inputArea = document.createElement("div");
    inputArea.style.cssText =
      "padding:12px;border-top:1px solid " + colors.border + ";display:flex;gap:8px;";
    inputArea.innerHTML =
      '<input id="dq-input" type="text" placeholder="Ask a question..." style="flex:1;padding:8px 12px;border:1px solid ' +
      colors.border +
      ";border-radius:6px;background:" +
      colors.input +
      ";color:" +
      colors.text +
      ';font-size:13px;outline:none;" />' +
      '<button id="dq-send" style="padding:8px 16px;background:' +
      colors.accent +
      ';color:#fff;border:none;border-radius:6px;font-size:13px;cursor:pointer;font-weight:500;">Send</button>';

    panel.appendChild(header);
    panel.appendChild(messagesArea);
    panel.appendChild(inputArea);

    document.body.appendChild(btn);
    document.body.appendChild(panel);

    // Event listeners
    document.getElementById("dq-close").addEventListener("click", toggleChat);
    document.getElementById("dq-send").addEventListener("click", sendMessage);
    document.getElementById("dq-input").addEventListener("keydown", function (e) {
      if (e.key === "Enter") sendMessage();
    });
  }

  function toggleChat() {
    isOpen = !isOpen;
    var panel = document.getElementById("dq-chat-panel");
    panel.style.display = isOpen ? "flex" : "none";
    if (isOpen) {
      document.getElementById("dq-input").focus();
    }
  }

  function appendMessage(role, text, sources, confidence) {
    var area = document.getElementById("dq-messages");
    var div = document.createElement("div");
    div.style.cssText =
      "margin-bottom:12px;padding:10px 12px;border-radius:8px;font-size:13px;line-height:1.5;max-width:90%;word-wrap:break-word;" +
      (role === "user"
        ? "background:" + colors.accent + ";color:#fff;margin-left:auto;"
        : "background:" + colors.input + ";color:" + colors.text + ";");
    div.textContent = text;

    if (sources && sources.length > 0) {
      var srcDiv = document.createElement("div");
      srcDiv.style.cssText = "margin-top:8px;font-size:11px;opacity:0.7;";
      srcDiv.innerHTML = sources
        .slice(0, 3)
        .map(function (s) {
          return '<a href="' + s.url + '" target="_blank" style="color:' + colors.accent + ';">' + s.title + "</a>";
        })
        .join(" | ");
      div.appendChild(srcDiv);
    }

    if (confidence && confidence !== "high") {
      var badge = document.createElement("span");
      badge.style.cssText =
        "display:inline-block;margin-top:6px;padding:2px 6px;border-radius:3px;font-size:10px;font-weight:600;" +
        (confidence === "low" ? "background:#fef2f2;color:#dc2626;" : "background:#fff7ed;color:#ea580c;");
      badge.textContent = confidence === "low" ? "Low confidence" : "Partial match";
      div.appendChild(badge);
    }

    area.appendChild(div);
    area.scrollTop = area.scrollHeight;
  }

  function sendMessage() {
    var input = document.getElementById("dq-input");
    var question = input.value.trim();
    if (!question) return;

    input.value = "";
    appendMessage("user", question);

    // Show loading
    var loadingId = "dq-loading-" + Date.now();
    var area = document.getElementById("dq-messages");
    var loading = document.createElement("div");
    loading.id = loadingId;
    loading.style.cssText =
      "margin-bottom:12px;padding:10px 12px;border-radius:8px;font-size:13px;background:" + colors.input + ";color:" + colors.text + ";opacity:0.6;";
    loading.textContent = "Thinking...";
    area.appendChild(loading);

    fetch(config.apiUrl + "/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: question,
        session_id: sessionId,
        collection: config.collection,
      }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var el = document.getElementById(loadingId);
        if (el) el.remove();
        appendMessage("assistant", data.answer, data.sources, data.confidence);
      })
      .catch(function () {
        var el = document.getElementById(loadingId);
        if (el) el.remove();
        appendMessage("assistant", "Sorry, I encountered an error. Please try again.");
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createWidget);
  } else {
    createWidget();
  }
})();
