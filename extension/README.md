# Job Applications Capture Extension

Chrome/Edge extension for capturing job ads and application emails while browsing.

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

Open an application-related email in Gmail, Outlook Web, or another webmail page and click
**Save Email**.

The extension tries to capture:

- subject
- sender
- visible email body, or selected text when you select part of the message
- received date when the page exposes a parseable date

Then it sends the payload to:

```text
http://127.0.0.1:8000/emails/import
```

For best results, open the individual email first. If a webmail layout is not detected well,
select the email body text before clicking **Save Email**.

## Packaging Notes

Browser-generated extension packages and keys are ignored by Git:

```text
*.crx
*.pem
```

Do not commit extension private keys.

