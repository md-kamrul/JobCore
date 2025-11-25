import React, { useState, useEffect } from "react";

const ProgressiveJobMessages = ({ jobMessages, delay = 1200 }) => {
  const [displayedMessages, setDisplayedMessages] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!jobMessages || jobMessages.length === 0) return;
    setDisplayedMessages([]);
    setCurrentIndex(0);
  }, [jobMessages]);

  useEffect(() => {
    if (!jobMessages || currentIndex >= jobMessages.length) return;
    const timer = setTimeout(() => {
      setDisplayedMessages((prev) => [...prev, jobMessages[currentIndex]]);
      setCurrentIndex((prev) => prev + 1);
    }, delay);
    return () => clearTimeout(timer);
  }, [currentIndex, jobMessages, delay]);

  return (
    <div className="progressive-job-messages">
      {displayedMessages.map((msg, idx) => (
        <div key={idx} className="job-message-bubble bg-[#161b22] text-gray-200 p-4 rounded-2xl mb-4">
          <pre className="whitespace-pre-line">{msg}</pre>
        </div>
      ))}
    </div>
  );
};

export default ProgressiveJobMessages;
