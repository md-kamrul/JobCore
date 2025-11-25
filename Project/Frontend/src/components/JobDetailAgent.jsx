import React, { useState } from "react";

/**
 * JobDetailAgent
 * Visits the job link and extracts detailed job info.
 * Props:
 *   jobUrl: string (URL of the job post)
 */
function JobDetailAgent({ jobUrl }) {
  const [jobDetails, setJobDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  React.useEffect(() => {
    if (!jobUrl) return;
    setLoading(true);
    setError(null);
    // Backend endpoint should fetch and parse job details from the jobUrl
    fetch(`http://localhost:5001/api/job-details?url=${encodeURIComponent(jobUrl)}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setJobDetails(data.details);
        } else {
          setError(data.message || "Failed to fetch job details.");
        }
      })
      .catch(() => setError("Unable to connect to job details service."))
      .finally(() => setLoading(false));
  }, [jobUrl]);

  if (!jobUrl) return null;
  if (loading) return <div>Loading job details...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!jobDetails) return null;

  return (
    <div className="job-detail-agent bg-[#161b22] text-gray-200 p-4 rounded-2xl mt-4">
      <h3>{jobDetails.title}</h3>
      <p><strong>Company:</strong> {jobDetails.company}</p>
      <p><strong>Type:</strong> {jobDetails.type}</p>
      <p><strong>Location:</strong> {jobDetails.location}</p>
      <p><strong>Experience Level:</strong> {jobDetails.experience_level}</p>
      <p><strong>Salary:</strong> {jobDetails.salary}</p>
      <a href={jobDetails.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 underline">View Job Posting</a>
    </div>
  );
}

export default JobDetailAgent;
