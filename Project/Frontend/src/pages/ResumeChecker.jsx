import { useState } from 'react';
import { FiUpload } from 'react-icons/fi';

export default function ResumeChecker() {
  const [file, setFile] = useState(null);
  const [position, setPosition] = useState('');
  const [description, setDescription] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.docx'))) {
      setFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleCheckResume = () => {
    if (file && position) {
      alert(`Checking resume for position: ${position}`);
    } else {
      alert('Please upload a resume and enter a target position.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-3">Resume Checker</h1>
          <p className="text-slate-400">Optimize your resume with AI to land your next interview.</p>
        </div>

        <div className="space-y-8">
          {/* Step 1: Upload Resume */}
          <div>
            <label className="block text-sm font-medium mb-3">Step 1: Upload Your Resume</label>
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition ${
                isDragging
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <FiUpload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-lg mb-2">
                {file ? file.name : 'Drag & drop your file here'}
              </p>
              <p className="text-sm text-slate-400 mb-4">Supports: PDF, DOCX</p>
              <label className="inline-block">
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <span className="px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded cursor-pointer transition inline-block">
                  Upload Resume
                </span>
              </label>
            </div>
          </div>

          {/* Step 2: Target Position */}
          <div>
            <label className="block text-sm font-medium mb-3">Step 2: Target Position</label>
            <input
              type="text"
              placeholder="e.g., Senior Product Manager"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Step 3: Job Description */}
          <div>
            <label className="block text-sm font-medium mb-3">
              Step 3: Job Description (Optional)
            </label>
            <textarea
              placeholder="Paste the full job description here..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
              className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Check Button */}
          <button
            onClick={handleCheckResume}
            className="w-full py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium transition text-lg"
          >
            Check My Resume
          </button>
        </div>
      </main>
    </div>
  );
}