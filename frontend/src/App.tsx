import { useEffect, useMemo, useState } from "react";
import {
  Application,
  ApplicationStatus,
  Email,
  EmailStatus,
  JobAd,
  JobAdStatus,
  MatchStatus,
  MatchingRunResult,
  confirmMatch,
  listApplications,
  listEmails,
  listJobAds,
  runMatching,
  updateApplication,
  updateEmail,
  updateJobAd
} from "./api";

type LoadState = "idle" | "loading" | "ready" | "error";

export function App() {
  const [jobs, setJobs] = useState<JobAd[]>([]);
  const [emails, setEmails] = useState<Email[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [message, setMessage] = useState<string>("Backend not checked yet.");
  const [matchingResult, setMatchingResult] = useState<MatchingRunResult | null>(null);
  const [manualJobId, setManualJobId] = useState<string>("");
  const [manualEmailId, setManualEmailId] = useState<string>("");

  async function refreshData() {
    setLoadState("loading");
    try {
      const [jobData, emailData, applicationData] = await Promise.all([
        listJobAds(),
        listEmails(),
        listApplications()
      ]);
      setJobs(jobData);
      setEmails(emailData);
      setApplications(applicationData);
      setMessage("Dashboard is up to date.");
      setLoadState("ready");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not reach backend.");
      setLoadState("error");
    }
  }

  async function handleRunMatching() {
    setMessage("Running matcher...");
    try {
      const result = await runMatching();
      setMatchingResult(result);
      setMessage("Matcher finished.");
      await refreshData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Matching failed.");
    }
  }

  async function handleJobStatusChange(jobId: number, status: JobAdStatus) {
    setMessage("Updating job...");
    try {
      await updateJobAd(jobId, { status });
      await refreshData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not update job.");
    }
  }

  async function handleEmailStatusChange(emailId: number, email_status: EmailStatus) {
    setMessage("Updating email...");
    try {
      await updateEmail(emailId, { email_status });
      await refreshData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not update email.");
    }
  }

  async function handleMatchStatusChange(emailId: number, match_status: MatchStatus) {
    setMessage("Updating match status...");
    try {
      await updateEmail(emailId, { match_status });
      await refreshData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not update match status.");
    }
  }

  async function handleApplicationStatusChange(applicationId: number, status: ApplicationStatus) {
    setMessage("Updating application...");
    try {
      await updateApplication(applicationId, { status });
      await refreshData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not update application.");
    }
  }

  async function handleConfirmMatch() {
    if (!manualJobId || !manualEmailId) {
      setMessage("Select a job and an email first.");
      return;
    }

    setMessage("Confirming match...");
    try {
      await confirmMatch(Number(manualJobId), Number(manualEmailId));
      setManualJobId("");
      setManualEmailId("");
      await refreshData();
      setMessage("Manual match confirmed.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not confirm match.");
    }
  }

  useEffect(() => {
    void refreshData();
  }, []);

  const summary = useMemo(() => {
    return {
      captured: jobs.length,
      notApplied: jobs.filter((job) => job.status === "not_applied").length,
      needsReview: emails.filter((email) => email.match_status === "needs_review").length,
      applications: applications.length,
      pending: applications.filter((application) => application.status === "pending").length,
      rejected: applications.filter((application) => application.status === "rejected").length,
      accepted: applications.filter((application) => application.status === "accepted").length
    };
  }, [applications, emails, jobs]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>Job Applications</h1>
          <p>{message}</p>
        </div>
        <div className="actions">
          <button type="button" onClick={() => void refreshData()} disabled={loadState === "loading"}>
            Refresh
          </button>
          <button type="button" className="primary" onClick={() => void handleRunMatching()}>
            Run matching
          </button>
        </div>
      </header>

      <section className="summary-grid" aria-label="Application summary">
        <Metric label="Captured jobs" value={summary.captured} />
        <Metric label="Not applied" value={summary.notApplied} />
        <Metric label="Applications" value={summary.applications} />
        <Metric label="Needs review" value={summary.needsReview} />
        <Metric label="Pending" value={summary.pending} />
        <Metric label="Rejected" value={summary.rejected} />
        <Metric label="Accepted" value={summary.accepted} />
      </section>

      {matchingResult ? (
        <section className="matching-result" aria-label="Latest matching result">
          <span>Processed {matchingResult.processed_count}</span>
          <span>Matched {matchingResult.matched_count}</span>
          <span>Review {matchingResult.needs_review_count}</span>
          <span>Unmatched {matchingResult.unmatched_count}</span>
        </section>
      ) : null}

      <section className="review-panel" aria-label="Manual match review">
        <div>
          <h2>Confirm Match</h2>
          <p>Connect an imported email to a captured job when automatic matching is uncertain.</p>
        </div>
        <div className="review-controls">
          <select value={manualJobId} onChange={(event) => setManualJobId(event.target.value)}>
            <option value="">Select job</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title} {job.company ? `- ${job.company}` : ""}
              </option>
            ))}
          </select>
          <select value={manualEmailId} onChange={(event) => setManualEmailId(event.target.value)}>
            <option value="">Select email</option>
            {emails.map((email) => (
              <option key={email.id} value={email.id}>
                {email.subject}
              </option>
            ))}
          </select>
          <button type="button" className="primary" onClick={() => void handleConfirmMatch()}>
            Confirm
          </button>
        </div>
      </section>

      <section className="layout">
        <Panel title="Captured Jobs">
          <JobTable jobs={jobs} onStatusChange={handleJobStatusChange} />
        </Panel>
        <Panel title="Emails">
          <EmailTable
            emails={emails}
            onEmailStatusChange={handleEmailStatusChange}
            onMatchStatusChange={handleMatchStatusChange}
          />
        </Panel>
        <Panel title="Applications">
          <ApplicationTable
            applications={applications}
            onStatusChange={handleApplicationStatusChange}
          />
        </Panel>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function JobTable({
  jobs,
  onStatusChange
}: {
  jobs: JobAd[];
  onStatusChange: (jobId: number, status: JobAdStatus) => void;
}) {
  if (jobs.length === 0) {
    return <EmptyState text="No captured jobs yet." />;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Role</th>
            <th>Company</th>
            <th>Location</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id}>
              <td>
                {job.url ? (
                  <a href={job.url} target="_blank" rel="noreferrer">
                    {job.title}
                  </a>
                ) : (
                  job.title
                )}
              </td>
              <td>{job.company ?? "-"}</td>
              <td>{job.location ?? "-"}</td>
              <td>
                <StatusSelect
                  value={job.status}
                  options={["not_applied", "applied", "rejected", "accepted", "archived"]}
                  onChange={(value) => onStatusChange(job.id, value as JobAdStatus)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function EmailTable({
  emails,
  onEmailStatusChange,
  onMatchStatusChange
}: {
  emails: Email[];
  onEmailStatusChange: (emailId: number, status: EmailStatus) => void;
  onMatchStatusChange: (emailId: number, status: MatchStatus) => void;
}) {
  if (emails.length === 0) {
    return <EmptyState text="No imported emails yet." />;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Subject</th>
            <th>Extracted</th>
            <th>Email</th>
            <th>Match</th>
          </tr>
        </thead>
        <tbody>
          {emails.map((email) => (
            <tr key={email.id}>
              <td>{email.subject}</td>
              <td>
                <div>{email.extracted_role_title ?? "-"}</div>
                <small>{email.extracted_company ?? ""}</small>
              </td>
              <td>
                <StatusSelect
                  value={email.email_status}
                  options={["pending", "rejected", "accepted", "unknown"]}
                  onChange={(value) => onEmailStatusChange(email.id, value as EmailStatus)}
                />
              </td>
              <td>
                <StatusSelect
                  value={email.match_status}
                  options={["not_set", "set", "needs_review"]}
                  onChange={(value) => onMatchStatusChange(email.id, value as MatchStatus)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ApplicationTable({
  applications,
  onStatusChange
}: {
  applications: Application[];
  onStatusChange: (applicationId: number, status: ApplicationStatus) => void;
}) {
  if (applications.length === 0) {
    return <EmptyState text="No applications yet." />;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Role</th>
            <th>Company</th>
            <th>Status</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((application) => (
            <tr key={application.id}>
              <td>{application.role_title ?? "-"}</td>
              <td>{application.company ?? "-"}</td>
              <td>
                <StatusSelect
                  value={application.status}
                  options={["applied", "pending", "rejected", "accepted", "unknown"]}
                  onChange={(value) => onStatusChange(application.id, value as ApplicationStatus)}
                />
              </td>
              <td>{formatDate(application.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Status({ value }: { value: string }) {
  return <span className={`status status-${value.replace("_", "-")}`}>{value.replace("_", " ")}</span>;
}

function StatusSelect({
  value,
  options,
  onChange
}: {
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="status-select">
      <Status value={value} />
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option.replace("_", " ")}
          </option>
        ))}
      </select>
    </label>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="empty-state">{text}</div>;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

