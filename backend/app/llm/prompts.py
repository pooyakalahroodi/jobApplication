JOB_AD_EXTRACTION_PROMPT = """
Extract structured job-ad information from the text below.
Return JSON with company, role_title, location, remote_policy, employment_type, and summary.
"""

EMAIL_EXTRACTION_PROMPT = """
Classify this job-related email.
Return JSON with email_status, company, role_title, next_action, and confidence.
"""

