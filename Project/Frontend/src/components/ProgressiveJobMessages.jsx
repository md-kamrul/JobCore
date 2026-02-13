
import React, { useState, useEffect } from "react";
import JobMessageAgent from "./JobMessageAgent";

// Helper: Parse markdown job string to job object
function parseJobMarkdown(md) {
  // Example format:
  // - **Title:** ...
  //   **Company:** ...
  //   **Type:** ...
  //   **Office:** ...
  //   **Location:** ...
  //   **Experience Level:** ...
  //   **Salary:** ...
  //   **Apply:** [url](url)
  const job = {};
  const lines = md.split("\n");
  lines.forEach(line => {
    if (line.includes("**Title:**")) job.title = line.split("**Title:**")[1]?.trim();
    if (line.includes("**Company:**")) job.company = line.split("**Company:**")[1]?.trim();
    if (line.includes("**Type:**")) job.type = line.split("**Type:**")[1]?.trim();
    if (line.includes("**Office:**")) job.office = line.split("**Office:**")[1]?.trim();
    if (line.includes("**Location:**")) job.location = line.split("**Location:**")[1]?.trim();
    if (line.includes("**Experience Level:**")) job.experience_level = line.split("**Experience Level:**")[1]?.trim();
    if (line.includes("**Salary:**")) job.salary = line.split("**Salary:**")[1]?.trim();
    if (line.includes("**Apply:**")) {
      const match = line.match(/\[(.*?)\]\((.*?)\)/);
      job.url = match ? match[2] : "";
    }
  });
  return job;
}

const ProgressiveJobMessages = ({ jobMessages, delay = 1200 }) => {
  const [displayedJobs, setDisplayedJobs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!jobMessages || jobMessages.length === 0) return;
    setDisplayedJobs([]);
    setCurrentIndex(0);
  }, [jobMessages]);

  useEffect(() => {
    if (!jobMessages || currentIndex >= jobMessages.length) return;
    const timer = setTimeout(() => {
      const jobObj = parseJobMarkdown(jobMessages[currentIndex]);
      setDisplayedJobs((prev) => [...prev, jobObj]);
      setCurrentIndex((prev) => prev + 1);
    }, delay);
    return () => clearTimeout(timer);
  }, [currentIndex, jobMessages, delay]);

  return (
    <div className="progressive-job-messages">
      <JobMessageAgent jobs={displayedJobs} />
    </div>
  );
};

export default ProgressiveJobMessages;
