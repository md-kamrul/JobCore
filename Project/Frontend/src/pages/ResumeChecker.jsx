import { useState } from 'react';
import { FiUpload, FiFileText, FiBriefcase, FiCheckCircle, FiXCircle, FiLoader, FiAlertCircle, FiTarget, FiList } from 'react-icons/fi';

export default function ResumeChecker() {
  const [file, setFile] = useState(null);
  const [position, setPosition] = useState('');
  const [description, setDescription] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

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
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('Please upload a PDF file');
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const parseAnalysisResponse = (text) => {
    try {
      // Try to parse as JSON first
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      
      // If not JSON, parse manually
      const jdMatch = text.match(/JD Match["\s:]*(\d+%)/i);
      const keywordsMatch = text.match(/MissingKeywords["\s:]*\[(.*?)\]/is);
      const summaryMatch = text.match(/Profile Summary["\s:]*["']?(.*?)["']?$/is);
      
      return {
        'JD Match': jdMatch ? jdMatch[1] : 'N/A',
        'MissingKeywords': keywordsMatch ? keywordsMatch[1].split(',').map(k => k.trim().replace(/['"]/g, '')) : [],
        'Profile Summary': summaryMatch ? summaryMatch[1].trim() : text
      };
    } catch (e) {
      // Return raw text if parsing fails
      return {
        'JD Match': 'N/A',
        'MissingKeywords': [],
        'Profile Summary': text
      };
    }
  };

  const handleCheckResume = async (analysisType = 'summary') => {
    if (!file || !position) {
      setError('Please upload a resume and enter a target position.');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('position', position);
    formData.append('description', description || '');
    formData.append('analysis_type', analysisType);

    try {
      const response = await fetch('http://localhost:5000/check_resume', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        const parsedAnalysis = parseAnalysisResponse(data.analysis || data.recommendation || '');
        setAnalysis({
          type: analysisType,
          data: parsedAnalysis,
          raw: data.analysis || data.recommendation
        });
        setActiveTab('summary');
      } else {
        setError(data.error || 'Failed to check resume');
      }
    } catch (err) {
      setError('Failed to connect to backend. Make sure the server is running on http://localhost:5000');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPosition('');
    setDescription('');
    setAnalysis(null);
    setError(null);
    setActiveTab('summary');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 text-white">
      <main className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-indigo-500/20 rounded-2xl">
              <FiFileText className="w-12 h-12 text-indigo-400" />
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            ATS Resume Expert
          </h1>
          <p className="text-slate-400 text-lg">
            AI-powered resume analysis to boost your job application success
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Left Column - Input Form */}
          <div className="space-y-6">
            {/* Step 1: Upload Resume */}
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700/50">
              <label className="block text-sm font-semibold mb-4 flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-500 text-xs">1</span>
                Upload Your Resume (PDF)
              </label>
              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
                  isDragging
                    ? 'border-indigo-500 bg-indigo-500/10 scale-105'
                    : 'border-slate-600 hover:border-slate-500 hover:bg-slate-700/30'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <FiUpload className="w-10 h-10 mx-auto mb-3 text-slate-400" />
                <p className="text-sm mb-1 font-medium">
                  {file ? (
                    <span className="text-indigo-400 flex items-center justify-center gap-2">
                      <FiCheckCircle className="w-4 h-4" />
                      {file.name}
                    </span>
                  ) : (
                    'Drag & drop your resume'
                  )}
                </p>
                <p className="text-xs text-slate-400 mb-3">PDF only</p>
                <label className="inline-block">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <span className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg cursor-pointer transition inline-block text-sm font-medium">
                    Browse Files
                  </span>
                </label>
              </div>
            </div>

            {/* Step 2: Target Position */}
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700/50">
              <label className="block text-sm font-semibold mb-4 flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-500 text-xs">2</span>
                Target Position
              </label>
              <div className="relative">
                <FiBriefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="e.g., Senior Software Engineer"
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition text-sm"
                />
              </div>
            </div>

            {/* Step 3: Job Description */}
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700/50">
              <label className="block text-sm font-semibold mb-4 flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-500 text-xs">3</span>
                Job Description <span className="text-slate-500 text-xs font-normal">(Optional)</span>
              </label>
              <textarea
                placeholder="Paste the job description here for better analysis..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={5}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition text-sm"
              />
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleCheckResume('summary')}
                disabled={loading || !file || !position}
                className="py-3 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed rounded-lg font-semibold transition shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2 text-sm"
              >
                {loading ? (
                  <>
                    <FiLoader className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <FiFileText className="w-4 h-4" />
                    Full Analysis
                  </>
                )}
              </button>
              <button
                onClick={() => handleCheckResume('percentage')}
                disabled={loading || !file || !position}
                className="py-3 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed rounded-lg font-semibold transition shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2 text-sm"
              >
                {loading ? (
                  <>
                    <FiLoader className="w-4 h-4 animate-spin" />
                    Checking...
                  </>
                ) : (
                  <>
                    <FiTarget className="w-4 h-4" />
                    Match %
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {/* Error Display */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 flex items-start gap-3">
                <FiXCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-400 mb-1">Error</p>
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              </div>
            )}

            {/* Analysis Results */}
            {analysis && (
              <div className="bg-slate-800/50 backdrop-blur rounded-xl border border-slate-700/50 overflow-hidden">
                <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border-b border-green-500/30 p-4 flex items-center gap-3">
                  <FiCheckCircle className="w-6 h-6 text-green-400" />
                  <div>
                    <p className="font-semibold text-green-400 text-lg">Analysis Complete!</p>
                    <p className="text-slate-300 text-xs">Review your results below</p>
                  </div>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-slate-700">
                  <button
                    onClick={() => setActiveTab('summary')}
                    className={`flex-1 py-3 px-4 text-sm font-medium transition ${
                      activeTab === 'summary'
                        ? 'bg-indigo-500/20 text-indigo-400 border-b-2 border-indigo-500'
                        : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/30'
                    }`}
                  >
                    <FiFileText className="inline w-4 h-4 mr-2" />
                    Summary
                  </button>
                  <button
                    onClick={() => setActiveTab('keywords')}
                    className={`flex-1 py-3 px-4 text-sm font-medium transition ${
                      activeTab === 'keywords'
                        ? 'bg-indigo-500/20 text-indigo-400 border-b-2 border-indigo-500'
                        : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/30'
                    }`}
                  >
                    <FiList className="inline w-4 h-4 mr-2" />
                    Keywords
                  </button>
                </div>

                {/* Tab Content */}
                <div className="p-6 max-h-96 overflow-y-auto">
                  {activeTab === 'summary' && (
                    <div className="space-y-4">
                      {/* Match Percentage */}
                      <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-slate-400 font-medium">JD Match Score</span>
                          <span className="text-2xl font-bold text-indigo-400">
                            {analysis.data['JD Match'] || 'N/A'}
                          </span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all"
                            style={{
                              width: analysis.data['JD Match'] || '0%'
                            }}
                          />
                        </div>
                      </div>

                      {/* Profile Summary */}
                      <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                        <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                          <FiAlertCircle className="w-4 h-4" />
                          Profile Summary
                        </h3>
                        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                          {analysis.data['Profile Summary'] || analysis.raw}
                        </p>
                      </div>
                    </div>
                  )}

                  {activeTab === 'keywords' && (
                    <div className="space-y-3">
                      <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                        <FiList className="w-4 h-4" />
                        Missing Keywords
                      </h3>
                      {analysis.data['MissingKeywords'] && analysis.data['MissingKeywords'].length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {analysis.data['MissingKeywords'].map((keyword, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1.5 bg-red-500/10 border border-red-500/30 text-red-300 rounded-lg text-xs font-medium"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-slate-400 text-sm">No missing keywords identified</p>
                      )}
                    </div>
                  )}
                </div>

                {/* Reset Button */}
                <div className="border-t border-slate-700 p-4">
                  <button
                    onClick={handleReset}
                    className="w-full px-4 py-2.5 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition text-sm"
                  >
                    Check Another Resume
                  </button>
                </div>
              </div>
            )}

            {/* Placeholder when no analysis */}
            {!analysis && !error && (
              <div className="bg-slate-800/30 backdrop-blur rounded-xl border border-slate-700/30 border-dashed p-12 text-center">
                <FiFileText className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                <p className="text-slate-500 text-sm">
                  Upload your resume and click analyze to see results here
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-slate-500 text-xs">
          <p>Powered by OpenAI GPT • Your data is processed securely</p>
        </div>
      </main>
    </div>
  );
}
