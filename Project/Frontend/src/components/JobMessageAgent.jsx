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
    return <div>No job results found.</div>;
  }
  return (
    <div className="job-message-agent">
      {jobs.map((job, idx) => (
        <div key={idx} className="job-message">
          <h3>{job.title}</h3>
          <p><strong>Company:</strong> {job.company}</p>
          <p><strong>Type:</strong> {job.type || 'N/A'}</p>
          <p><strong>Location:</strong> {job.location}</p>
          <p><strong>Experience Level:</strong> {job.experience_level || 'N/A'}</p>
          <p><strong>Salary:</strong> {job.salary || 'N/A'}</p>
          {job.url && (
            <a href={job.url} target="_blank" rel="noopener noreferrer">Apply</a>
          )}
        </div>
      ))}
    </div>
  );
}

export default JobMessageAgent;
