const backendUrl = "http://127.0.0.1:8000/job-ads/capture";
const saveButton = document.getElementById("saveJob");
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

async function saveJob() {
  saveButton.disabled = true;
  setStatus("Capturing page...");

  try {
    const tab = await getActiveTab();
    const payload = await collectJobPageData(tab.id);
    setStatus("Saving to local dashboard...");

    const response = await fetch(backendUrl, {
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
    saveButton.disabled = false;
  }
}

saveButton.addEventListener("click", saveJob);

