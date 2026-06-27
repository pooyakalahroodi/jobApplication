# Job Applications Capture Extension

Chrome/Edge extension for capturing job ads while browsing.

## Local Setup

1. Start the backend:

   ```powershell
   cd backend
   .\.venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. Open Chrome or Edge extensions:

   ```text
   chrome://extensions
   edge://extensions
   ```

3. Enable Developer Mode.
4. Click **Load unpacked**.
5. Select this folder:

   ```text
   extension/
   ```

## Usage

Open a job advertisement page and click **Save Job**.

The extension captures:

- current URL
- browser page title
- selected text
- visible page text
- JSON-LD metadata
- capture timestamp

Then it sends the payload to:

```text
http://127.0.0.1:8000/job-ads/capture
```

