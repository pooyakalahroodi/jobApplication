const jobCaptureUrl = "http://127.0.0.1:8000/job-ads/capture";
const emailImportUrl = "http://127.0.0.1:8000/emails/import";
const saveButton = document.getElementById("saveJob");
const saveEmailButton = document.getElementById("saveEmail");
const statusText = document.getElementById("status");

function setStatus(message) {
  statusText.textContent = message;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function collectJobPageData(tabId) {
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const jsonLd = Array.from(
        document.querySelectorAll('script[type="application/ld+json"]')
      )
        .map((script) => {
          try {
            return JSON.parse(script.textContent || "{}");
          } catch {
            return null;
          }
        })
        .filter(Boolean)
        .flat();

      const selectedText = window.getSelection()?.toString().trim() || null;
      const rawText = document.body?.innerText?.trim() || null;
      const jobPosting = jsonLd.find((item) => item["@type"] === "JobPosting") || null;

      return {
        url: window.location.href,
        title: jobPosting?.title || document.title || "Untitled job",
        company: jobPosting?.hiringOrganization?.name || null,
        location:
          jobPosting?.jobLocation?.address?.addressLocality ||
          jobPosting?.jobLocation?.address?.addressRegion ||
          null,
        source: "browser_extension",
        page_title: document.title || null,
        selected_text: selectedText,
        raw_text: rawText,
        json_ld: jsonLd,
        captured_at: new Date().toISOString()
      };
    }
  });

  return result.result;
}

async function collectEmailPageData(tabId) {
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      function textFromSelectors(selectors) {
        for (const selector of selectors) {
          const element = document.querySelector(selector);
          const text = element?.innerText?.trim() || element?.textContent?.trim();
          if (text) {
            return text;
          }
        }
        return null;
      }

      function attrFromSelectors(selectors, attr) {
        for (const selector of selectors) {
          const element = document.querySelector(selector);
          const value = element?.getAttribute?.(attr);
          if (value) {
            return value;
          }
        }
        return null;
      }

      function isoDateOrNull(value) {
        if (!value) {
          return null;
        }
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
      }

      const host = window.location.hostname;
      const selectedText = window.getSelection()?.toString().trim() || null;
      const isGmail = host.includes("mail.google.");
      const isOutlook = host.includes("outlook.") || host.includes("office.com");

      const subject = textFromSelectors([
        "h2.hP",
        '[data-testid="message-subject"]',
        '[role="main"] h1',
        "h1"
      ]);
      const sender =
        attrFromSelectors([".gD[email]", '[email][name]', '[data-testid="message-header"] [title]'], "email") ||
        attrFromSelectors([".gD[title]", '[data-testid="message-header"] [title]'], "title") ||
        textFromSelectors([".gD", '[data-testid="message-header"]']);
      const body = selectedText || textFromSelectors([
        ".a3s.aiL",
        '[role="document"]',
        '[aria-label="Message body"]',
        '[data-testid="message-body"]',
        "main"
      ]);
      const dateText =
        attrFromSelectors([".g3[title]", "time[datetime]"], "title") ||
        attrFromSelectors(["time[datetime]"], "datetime") ||
        textFromSelectors([".g3", "time"]);
      const receivedAt = isoDateOrNull(dateText);

      return {
        subject: subject || document.title || "Untitled email",
        sender: sender || null,
        body: body || document.body?.innerText?.trim() || "",
        received_at: receivedAt,
        capture_source: isGmail ? "gmail_web" : isOutlook ? "outlook_web" : "browser_page",
        page_url: window.location.href
      };
    }
  });

  return result.result;
}

async function saveJob() {
  setButtonsDisabled(true);
  setStatus("Capturing page...");

  try {
    const tab = await getActiveTab();
    const payload = await collectJobPageData(tab.id);
    setStatus("Saving to local dashboard...");

    const response = await fetch(jobCaptureUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    setStatus("Saved. You can close this popup.");
  } catch (error) {
    setStatus(`Could not save job. ${error.message}`);
  } finally {
    setButtonsDisabled(false);
  }
}

async function saveEmail() {
  setButtonsDisabled(true);
  setStatus("Capturing email...");

  try {
    const tab = await getActiveTab();
    const payload = await collectEmailPageData(tab.id);
    if (!payload.body.trim()) {
      throw new Error("No email body found. Open the email or select the email text first.");
    }

    setStatus("Saving email to local dashboard...");
    const response = await fetch(emailImportUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subject: payload.subject,
        sender: payload.sender,
        body: payload.body,
        received_at: payload.received_at
      })
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    setStatus("Email saved. You can close this popup.");
  } catch (error) {
    setStatus(`Could not save email. ${error.message}`);
  } finally {
    setButtonsDisabled(false);
  }
}

function setButtonsDisabled(disabled) {
  saveButton.disabled = disabled;
  saveEmailButton.disabled = disabled;
}

saveButton.addEventListener("click", saveJob);
saveEmailButton.addEventListener("click", saveEmail);

