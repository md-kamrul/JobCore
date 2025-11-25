// JobMessageAgent.jsx
import React from 'react';

/**
 * JobMessageAgent
 * Displays each job post as a separate message to the user, showing only required info.
 * Props:
 *   jobs: Array of job objects (title, company, type, location, experience_level, salary, url)
 */
function JobMessageAgent({ jobs }) {
  if (!jobs || jobs.length === 0) {
    return <div className="job-message-agent-empty">No job results found.</div>;
  }
  return (
    <div className="job-message-agent">
      {jobs.map((job, idx) => (
        <div key={idx} className="job-message-card">
          <div className="job-message-header">
            {/* Logo/Icon */}
            <div className="job-message-logo">
              {job.logoUrl ? (
                <img src={job.logoUrl} alt={job.company + ' logo'} />
              ) : (
                <div className="job-message-logo-placeholder">{job.company?.[0] || "J"}</div>
              )}
            </div>
            <div className="job-message-info">
              <div className="job-message-time-badge">
                {job.postedTime && <span className="badge badge-time">{job.postedTime}</span>}
                {job.earlyApplicant && <span className="badge badge-early">Be an early applicant</span>}
              </div>
              <h3 className="job-message-title">{job.title}</h3>
              <div className="job-message-company">{job.company}</div>
              <div className="job-message-tags">
                {job.industry && <span className="badge badge-industry">{job.industry}</span>}
                {job.stage && <span className="badge badge-stage">{job.stage}</span>}
              </div>
            </div>
          </div>
          <div className="job-message-details">
            <div className="job-message-badges">
              {job.location && <span className="badge badge-location">{job.location}</span>}
              {job.remote && <span className="badge badge-remote">Remote</span>}
              {job.type && <span className="badge badge-type">{job.type}</span>}
              {job.contract && <span className="badge badge-contract">Contract</span>}
              {job.experience_level && <span className="badge badge-experience">{job.experience_level}</span>}
            </div>
            {job.salary && <div className="job-message-salary">💰 {job.salary}</div>}
          </div>
          <div className="job-message-actions">
            {job.url && (
              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="job-message-apply-btn"
              >
                APPLY NOW
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default JobMessageAgent;
