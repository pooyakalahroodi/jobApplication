import { useEffect, useMemo, useState } from "react";
import {
  Application,
  ApplicationDetail,
  ApplicationStatus,
  Email,
  EmailStatus,
  ExtractionRun,
  JobAd,
  JobAdStatus,
  MatchStatus,
  MatchingRunResult,
  confirmMatch,
  deleteApplication,
  deleteEmail,
  deleteJobAd,
  extractEmail,
  extractJobAd,
  getApplicationDetail,
  listExtractionRuns,
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
  const [extractionRuns, setExtractionRuns] = useState<ExtractionRun[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [message, setMessage] = useState<string>("Backend not checked yet.");
  const [matchingResult, setMatchingResult] = useState<MatchingRunResult | null>(null);
  const [manualJobId, setManualJobId] = useState<string>("");
  const [manualEmailId, setManualEmailId] = useState<string>("");
  const [selectedExtractionRunId, setSelectedExtractionRunId] = useState<number | null>(null);
  const [selectedApplicationDetail, setSelectedApplicationDetail] = useState<ApplicationDetail | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobAd | null>(null);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [jobStatusFilter, setJobStatusFilter] = useState<string>("available");
  const [emailStatusFilter, setEmailStatusFilter] = useState<string>("unmatched");
  const [applicationStatusFilter, setApplicationStatusFilter] = useState<string>("all");

  async function refreshData() {
    setLoadState("loading");
    try {
      const [jobData, emailData, applicationData, extractionRunData] = await Promise.all([
        listJobAds(),
        listEmails(),
        listApplications(),
        listExtractionRuns()
      ]);
      setJobs(jobData);
      setEmails(emailData);
      setApplications(applicationData);
      setExtractionRuns(extractionRunData);
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

  async function handleApplicationNotesSave(applicationId: number, manual_notes: string) {
    setMessage("Saving application notes...");
    try {
      const updatedApplication = await updateApplication(applicationId, {
        manual_notes: manual_notes.trim() === "" ? null : manual_notes
      });
      setSelectedApplicationDetail((current) =>
        current?.id === applicationId ? { ...current, ...updatedApplication } : current
      );
      await refreshData();
      setMessage("Application notes saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not save application notes.");
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

  async function handleExtractJob(jobId: number) {
    setMessage("Running local LLM for job...");
    try {
      await extractJobAd(jobId);
      await refreshData();
      setMessage("Job extraction finished.");
    } catch (error) {
      await refreshData();
      setMessage(error instanceof Error ? error.message : "Job extraction failed.");
    }
  }

  async function handleExtractEmail(emailId: number) {
    setMessage("Running local LLM for email...");
    try {
      await extractEmail(emailId);
      await refreshData();
      setMessage("Email extraction finished.");
    } catch (error) {
      await refreshData();
      setMessage(error instanceof Error ? error.message : "Email extraction failed.");
    }
  }

  async function handleViewApplication(applicationId: number) {
    setMessage("Loading application details...");
    try {
      const detail = await getApplicationDetail(applicationId);
      setSelectedApplicationDetail(detail);
      setMessage("Application details loaded.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load application details.");
    }
  }

  async function handleDeleteJob(jobId: number) {
    if (!window.confirm("Delete this captured job? Existing application records will stay.")) {
      return;
    }
    setMessage("Deleting job...");
    try {
      await deleteJobAd(jobId);
      await refreshData();
      setMessage("Job deleted.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not delete job.");
    }
  }

  async function handleDeleteEmail(emailId: number) {
    if (!window.confirm("Delete this email? Existing application timeline entries will stay.")) {
      return;
    }
    setMessage("Deleting email...");
    try {
      await deleteEmail(emailId);
      await refreshData();
      setMessage("Email deleted.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not delete email.");
    }
  }

  async function handleDeleteApplication(applicationId: number) {
    if (!window.confirm("Delete this application record?")) {
      return;
    }
    setMessage("Deleting application...");
    try {
      await deleteApplication(applicationId);
      if (selectedApplicationDetail?.id === applicationId) {
        setSelectedApplicationDetail(null);
      }
      await refreshData();
      setMessage("Application deleted.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not delete application.");
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

  const latestExtractionBySource = useMemo(() => {
    const map = new Map<string, ExtractionRun>();
    for (const run of extractionRuns) {
      const key = `${run.source_type}:${run.source_id}`;
      if (!map.has(key)) {
        map.set(key, run);
      }
    }
    return map;
  }, [extractionRuns]);

  const selectedExtractionRun = useMemo(() => {
    return extractionRuns.find((run) => run.id === selectedExtractionRunId) ?? null;
  }, [extractionRuns, selectedExtractionRunId]);

  const assignedJobIds = useMemo(() => {
    return new Set(applications.map((application) => application.job_ad_id).filter(Boolean));
  }, [applications]);

  const availableJobs = useMemo(() => {
    return jobs.filter((job) => job.status === "not_applied" && !assignedJobIds.has(job.id));
  }, [assignedJobIds, jobs]);

  const availableEmails = useMemo(() => {
    return emails.filter((email) => email.match_status !== "set");
  }, [emails]);

  const normalizedSearch = searchQuery.trim().toLowerCase();
  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      const text = [job.title, job.company, job.location, job.description, job.url]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      const matchesSearch = normalizedSearch === "" || text.includes(normalizedSearch);
      const matchesStatus =
        jobStatusFilter === "available"
          ? job.status === "not_applied" && !assignedJobIds.has(job.id)
          : jobStatusFilter === "all" || job.status === jobStatusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [assignedJobIds, jobStatusFilter, jobs, normalizedSearch]);

  const filteredEmails = useMemo(() => {
    return emails.filter((email) => {
      const text = [
        email.subject,
        email.sender,
        email.body,
        email.extracted_company,
        email.extracted_role_title
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      const matchesSearch = normalizedSearch === "" || text.includes(normalizedSearch);
      const matchesStatus =
        emailStatusFilter === "unmatched"
          ? email.match_status !== "set"
          : emailStatusFilter === "all" || email.email_status === emailStatusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [emailStatusFilter, emails, normalizedSearch]);

  const filteredApplications = useMemo(() => {
    return applications.filter((application) => {
      const text = [application.role_title, application.company].filter(Boolean).join(" ").toLowerCase();
      const matchesSearch = normalizedSearch === "" || text.includes(normalizedSearch);
      const matchesStatus =
        applicationStatusFilter === "all" || application.status === applicationStatusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [applicationStatusFilter, applications, normalizedSearch]);

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
        <Metric label="Available jobs" value={availableJobs.length} />
        <Metric label="Applications" value={summary.applications} />
        <Metric label="Open emails" value={availableEmails.length} />
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

      <section className="filter-bar" aria-label="Dashboard filters">
        <label className="search-field">
          <span>Search</span>
          <input
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Role, company, email text..."
          />
        </label>
        <label>
          <span>Jobs</span>
          <select value={jobStatusFilter} onChange={(event) => setJobStatusFilter(event.target.value)}>
            <option value="all">All jobs</option>
            <option value="available">Available</option>
            <option value="not_applied">Not applied</option>
            <option value="applied">Applied</option>
            <option value="rejected">Rejected</option>
            <option value="accepted">Accepted</option>
            <option value="archived">Archived</option>
          </select>
        </label>
        <label>
          <span>Emails</span>
          <select value={emailStatusFilter} onChange={(event) => setEmailStatusFilter(event.target.value)}>
            <option value="all">All emails</option>
            <option value="unmatched">Unmatched</option>
            <option value="pending">Pending</option>
            <option value="rejected">Rejected</option>
            <option value="accepted">Accepted</option>
            <option value="unknown">Unknown</option>
          </select>
        </label>
        <label>
          <span>Applications</span>
          <select
            value={applicationStatusFilter}
            onChange={(event) => setApplicationStatusFilter(event.target.value)}
          >
            <option value="all">All applications</option>
            <option value="applied">Applied</option>
            <option value="pending">Pending</option>
            <option value="rejected">Rejected</option>
            <option value="accepted">Accepted</option>
            <option value="unknown">Unknown</option>
          </select>
        </label>
      </section>

      <section className="review-panel workbench-panel" aria-label="Manual match review">
        <div>
          <h2>Review Queue</h2>
          <p>Match only open jobs and unassigned emails. Confirmed pairs move into Applications.</p>
        </div>
        <div className="review-controls">
          <select value={manualJobId} onChange={(event) => setManualJobId(event.target.value)}>
            <option value="">Select job</option>
            {availableJobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title} {job.company ? `- ${job.company}` : ""}
              </option>
            ))}
          </select>
          <select value={manualEmailId} onChange={(event) => setManualEmailId(event.target.value)}>
            <option value="">Select email</option>
            {availableEmails.map((email) => (
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
        <Panel title={`Available Jobs (${filteredJobs.length})`}>
          <JobTable
            jobs={filteredJobs}
            extractionRuns={latestExtractionBySource}
            onStatusChange={handleJobStatusChange}
            onExtract={handleExtractJob}
            onViewExtraction={setSelectedExtractionRunId}
            onView={setSelectedJob}
            onDelete={handleDeleteJob}
          />
        </Panel>
        <Panel title={`Open Emails (${filteredEmails.length})`}>
          <EmailTable
            emails={filteredEmails}
            extractionRuns={latestExtractionBySource}
            onEmailStatusChange={handleEmailStatusChange}
            onMatchStatusChange={handleMatchStatusChange}
            onExtract={handleExtractEmail}
            onViewExtraction={setSelectedExtractionRunId}
            onView={setSelectedEmail}
            onDelete={handleDeleteEmail}
          />
        </Panel>
        <Panel title={`Applications (${filteredApplications.length})`}>
          <ApplicationTable
            applications={filteredApplications}
            onStatusChange={handleApplicationStatusChange}
            onView={handleViewApplication}
            onDelete={handleDeleteApplication}
          />
        </Panel>
      </section>

      <Modal open={selectedJob !== null} onClose={() => setSelectedJob(null)}>
        <JobDetailsPanel job={selectedJob} onClose={() => setSelectedJob(null)} />
      </Modal>
      <Modal open={selectedEmail !== null} onClose={() => setSelectedEmail(null)}>
        <EmailDetailsPanel email={selectedEmail} onClose={() => setSelectedEmail(null)} />
      </Modal>
      <Modal open={selectedApplicationDetail !== null} onClose={() => setSelectedApplicationDetail(null)}>
        <ApplicationDetailsPanel
          detail={selectedApplicationDetail}
          onClose={() => setSelectedApplicationDetail(null)}
          onSaveNotes={handleApplicationNotesSave}
        />
      </Modal>
      <Modal open={selectedExtractionRun !== null} onClose={() => setSelectedExtractionRunId(null)}>
        <ExtractionDetailsPanel
          run={selectedExtractionRun}
          onClose={() => setSelectedExtractionRunId(null)}
        />
      </Modal>
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
  extractionRuns,
  onStatusChange,
  onExtract,
  onViewExtraction,
  onView,
  onDelete
}: {
  jobs: JobAd[];
  extractionRuns: Map<string, ExtractionRun>;
  onStatusChange: (jobId: number, status: JobAdStatus) => void;
  onExtract: (jobId: number) => void;
  onViewExtraction: (runId: number) => void;
  onView: (job: JobAd) => void;
  onDelete: (jobId: number) => void;
}) {
  if (jobs.length === 0) {
    return <EmptyState text="No captured jobs yet." />;
  }

  return (
    <div className="record-list">
      {jobs.map((job) => (
        <article className="record-card" key={job.id}>
          <div className="record-main">
            <div>
              <h3>
                {job.url ? (
                  <a href={job.url} target="_blank" rel="noreferrer">
                    {job.title}
                  </a>
                ) : (
                  job.title
                )}
              </h3>
              <p>
                {job.company ?? "Unknown company"}
                {job.location ? ` - ${job.location}` : ""}
              </p>
            </div>
            <StatusSelect
              value={job.status}
              options={["not_applied", "applied", "rejected", "accepted", "archived"]}
              onChange={(value) => onStatusChange(job.id, value as JobAdStatus)}
            />
          </div>
          <p className="record-preview">{job.description ?? job.selected_text ?? job.raw_text ?? "No description captured."}</p>
          <div className="record-footer">
            <ExtractionAction
              run={extractionRuns.get(`job_ad:${job.id}`)}
              onExtract={() => onExtract(job.id)}
              onView={onViewExtraction}
            />
            <div className="row-actions">
              <button type="button" onClick={() => onView(job)}>
                View
              </button>
              <button type="button" className="danger-button" onClick={() => onDelete(job.id)}>
                Delete
              </button>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

function EmailTable({
  emails,
  extractionRuns,
  onEmailStatusChange,
  onMatchStatusChange,
  onExtract,
  onViewExtraction,
  onView,
  onDelete
}: {
  emails: Email[];
  extractionRuns: Map<string, ExtractionRun>;
  onEmailStatusChange: (emailId: number, status: EmailStatus) => void;
  onMatchStatusChange: (emailId: number, status: MatchStatus) => void;
  onExtract: (emailId: number) => void;
  onViewExtraction: (runId: number) => void;
  onView: (email: Email) => void;
  onDelete: (emailId: number) => void;
}) {
  if (emails.length === 0) {
    return <EmptyState text="No imported emails yet." />;
  }

  return (
    <div className="record-list">
      {emails.map((email) => (
        <article className="record-card" key={email.id}>
          <div className="record-main">
            <div>
              <h3>{email.subject}</h3>
              <p>
                {email.sender ?? "Unknown sender"}
                {email.extracted_role_title ? ` - ${email.extracted_role_title}` : ""}
                {email.extracted_company ? ` - ${email.extracted_company}` : ""}
              </p>
            </div>
            <div className="status-stack">
              <StatusSelect
                value={email.email_status}
                options={["pending", "rejected", "accepted", "unknown"]}
                onChange={(value) => onEmailStatusChange(email.id, value as EmailStatus)}
              />
              <StatusSelect
                value={email.match_status}
                options={["not_set", "set", "needs_review"]}
                onChange={(value) => onMatchStatusChange(email.id, value as MatchStatus)}
              />
            </div>
          </div>
          <p className="record-preview">{email.body}</p>
          <div className="record-footer">
            <ExtractionAction
              run={extractionRuns.get(`email:${email.id}`)}
              onExtract={() => onExtract(email.id)}
              onView={onViewExtraction}
            />
            <div className="row-actions">
              <button type="button" onClick={() => onView(email)}>
                View
              </button>
              <button type="button" className="danger-button" onClick={() => onDelete(email.id)}>
                Delete
              </button>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

function ApplicationTable({
  applications,
  onStatusChange,
  onView,
  onDelete
}: {
  applications: Application[];
  onStatusChange: (applicationId: number, status: ApplicationStatus) => void;
  onView: (applicationId: number) => void;
  onDelete: (applicationId: number) => void;
}) {
  if (applications.length === 0) {
    return <EmptyState text="No applications yet." />;
  }

  return (
    <div className="record-list">
      {applications.map((application) => (
        <article className="record-card" key={application.id}>
          <div className="record-main">
            <div>
              <h3>{application.role_title ?? "Untitled application"}</h3>
              <p>
                {application.company ?? "Unknown company"} - Updated {formatDate(application.updated_at)}
              </p>
            </div>
            <StatusSelect
              value={application.status}
              options={["applied", "pending", "rejected", "accepted", "unknown"]}
              onChange={(value) => onStatusChange(application.id, value as ApplicationStatus)}
            />
          </div>
          <div className="record-footer">
            <span className="record-meta">Created {formatDate(application.created_at)}</span>
            <div className="row-actions">
              <button type="button" onClick={() => onView(application.id)}>
                View
              </button>
              <button
                type="button"
                className="danger-button"
                onClick={() => onDelete(application.id)}
              >
                Delete
              </button>
            </div>
          </div>
        </article>
      ))}
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

function Modal({
  open,
  children,
  onClose
}: {
  open: boolean;
  children: React.ReactNode;
  onClose: () => void;
}) {
  if (!open) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div className="modal-panel" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}

function JobDetailsPanel({ job, onClose }: { job: JobAd | null; onClose: () => void }) {
  if (!job) {
    return null;
  }

  return (
    <section className="details-panel" aria-label="Captured job details">
      <header>
        <div>
          <h2>Captured Job</h2>
          <p>{job.company ?? "Unknown company"}</p>
        </div>
        <button type="button" onClick={onClose}>
          Close
        </button>
      </header>
      <div className="details-grid">
        <Detail label="Status" value={job.status} />
        <Detail label="Company" value={job.company ?? "-"} />
        <Detail label="Location" value={job.location ?? "-"} />
        <Detail label="Captured" value={formatDate(job.captured_at ?? job.created_at)} />
      </div>
      <div className="detail-block">
        <h3>Position</h3>
        <p>
          {job.url ? (
            <a href={job.url} target="_blank" rel="noreferrer">
              {job.title}
            </a>
          ) : (
            job.title
          )}
        </p>
      </div>
      <div className="detail-block">
        <h3>Extracted Description</h3>
        <p>{job.description ?? job.selected_text ?? "No description saved yet."}</p>
      </div>
      {job.raw_text ? (
        <div className="detail-block">
          <h3>Captured Page Text</h3>
          <pre>{job.raw_text}</pre>
        </div>
      ) : null}
      {job.json_ld ? (
        <div className="detail-block">
          <h3>Structured Page Data</h3>
          <pre>{JSON.stringify(job.json_ld, null, 2)}</pre>
        </div>
      ) : null}
    </section>
  );
}

function EmailDetailsPanel({ email, onClose }: { email: Email | null; onClose: () => void }) {
  if (!email) {
    return null;
  }

  return (
    <section className="details-panel" aria-label="Email details">
      <header>
        <div>
          <h2>Email Details</h2>
          <p>{email.sender ?? "Unknown sender"}</p>
        </div>
        <button type="button" onClick={onClose}>
          Close
        </button>
      </header>
      <div className="details-grid">
        <Detail label="Email status" value={email.email_status} />
        <Detail label="Match status" value={email.match_status} />
        <Detail
          label="Confidence"
          value={
            email.extraction_confidence !== null
              ? `${Math.round(email.extraction_confidence * 100)}%`
              : "-"
          }
        />
        <Detail label="Received" value={email.received_at ? formatDate(email.received_at) : "-"} />
      </div>
      <div className="detail-block">
        <h3>Subject</h3>
        <p>{email.subject}</p>
      </div>
      <div className="details-grid">
        <Detail label="Extracted company" value={email.extracted_company ?? "-"} />
        <Detail label="Extracted role" value={email.extracted_role_title ?? "-"} />
      </div>
      <div className="detail-block">
        <h3>Email Body</h3>
        <pre>{email.body}</pre>
      </div>
    </section>
  );
}

function ApplicationDetailsPanel({
  detail,
  onClose,
  onSaveNotes
}: {
  detail: ApplicationDetail | null;
  onClose: () => void;
  onSaveNotes: (applicationId: number, manualNotes: string) => Promise<void>;
}) {
  const [manualNotes, setManualNotes] = useState("");

  useEffect(() => {
    setManualNotes(detail?.manual_notes ?? "");
  }, [detail]);

  if (!detail) {
    return null;
  }

  return (
    <section className="details-panel" aria-label="Application details">
      <header>
        <div>
          <h2>Application Details</h2>
          <p>
            {detail.role_title ?? "-"} {detail.company ? `- ${detail.company}` : ""}
          </p>
        </div>
        <button type="button" onClick={onClose}>
          Close
        </button>
      </header>
      <div className="details-grid">
        <Detail label="Status" value={detail.status} />
        <Detail label="Company" value={detail.company ?? "-"} />
        <Detail label="Role" value={detail.role_title ?? "-"} />
        <Detail label="Updated" value={formatDate(detail.updated_at)} />
      </div>
      {detail.job_ad ? (
        <div className="detail-block">
          <h3>Captured Job</h3>
          <p>
            {detail.job_ad.url ? (
              <a href={detail.job_ad.url} target="_blank" rel="noreferrer">
                {detail.job_ad.title}
              </a>
            ) : (
              detail.job_ad.title
            )}
            {detail.job_ad.location ? ` - ${detail.job_ad.location}` : ""}
          </p>
        </div>
      ) : null}
      <div className="detail-block notes-editor">
        <div className="detail-block-heading">
          <h3>Personal Notes</h3>
          <button type="button" className="primary" onClick={() => void onSaveNotes(detail.id, manualNotes)}>
            Save Notes
          </button>
        </div>
        <textarea
          value={manualNotes}
          onChange={(event) => setManualNotes(event.target.value)}
          placeholder="Add form answers, recruiter details, interview preparation notes..."
        />
      </div>
      <div className="detail-block">
        <h3>Timeline</h3>
        {detail.events.length > 0 ? (
          <ol className="timeline">
            {detail.events.map((event) => (
              <li key={event.id}>
                <strong>{event.event_type.replace("_", " ")}</strong>
                <span>{formatDate(event.event_date ?? event.created_at)}</span>
                {event.notes ? <p>{event.notes}</p> : null}
              </li>
            ))}
          </ol>
        ) : (
          <p>No timeline events yet.</p>
        )}
      </div>
    </section>
  );
}

function ExtractionAction({
  run,
  onExtract,
  onView
}: {
  run: ExtractionRun | undefined;
  onExtract: () => void;
  onView: (runId: number) => void;
}) {
  return (
    <div className="extraction-action">
      <button type="button" onClick={onExtract}>
        Extract
      </button>
      {run ? (
        <small className={run.status === "success" ? "run-success" : "run-failed"}>
          {run.status}
          {run.confidence !== null ? ` ${Math.round(run.confidence * 100)}%` : ""}
        </small>
      ) : (
        <small>not run</small>
      )}
      {run ? (
        <button type="button" className="text-button" onClick={() => onView(run.id)}>
          View
        </button>
      ) : null}
    </div>
  );
}

function ExtractionDetailsPanel({
  run,
  onClose
}: {
  run: ExtractionRun | null;
  onClose: () => void;
}) {
  if (!run) {
    return null;
  }

  const evidence = typeof run.parsed_json?.evidence === "string" ? run.parsed_json.evidence : null;

  return (
    <section className="details-panel" aria-label="Extraction details">
      <header>
        <div>
          <h2>Extraction Details</h2>
          <p>
            {run.source_type.replace("_", " ")} #{run.source_id} via {run.model ?? run.extractor}
          </p>
        </div>
        <button type="button" onClick={onClose}>
          Close
        </button>
      </header>
      <div className="details-grid">
        <Detail label="Status" value={run.status} />
        <Detail
          label="Confidence"
          value={run.confidence !== null ? `${Math.round(run.confidence * 100)}%` : "-"}
        />
        <Detail label="Prompt" value={run.prompt_version} />
        <Detail label="Created" value={formatDate(run.created_at)} />
      </div>
      {evidence ? (
        <div className="detail-block">
          <h3>Evidence</h3>
          <p>{evidence}</p>
        </div>
      ) : null}
      {run.error_message ? (
        <div className="detail-block error-block">
          <h3>Error</h3>
          <p>{run.error_message}</p>
        </div>
      ) : null}
      <div className="detail-block">
        <h3>Parsed JSON</h3>
        <pre>{JSON.stringify(run.parsed_json, null, 2)}</pre>
      </div>
      {run.raw_output ? (
        <div className="detail-block">
          <h3>Raw Output</h3>
          <pre>{run.raw_output}</pre>
        </div>
      ) : null}
    </section>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
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

