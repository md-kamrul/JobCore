import React, { useState, useEffect, useRef } from "react";

const API_BASE = (import.meta.env.VITE_MOCK_INTERVIEW_API_URL || "http://localhost:5002").replace(/\/$/, "");

// ── Styles ──────────────────────────────────────────────────────
const styles = {
  page: {
    minHeight: "100vh",
    background: "#0a0f1a",
    color: "#e2e8f0",
    fontFamily: "'Segoe UI', system-ui, sans-serif",
  },
  container: {
    maxWidth: "900px",
    margin: "0 auto",
    padding: "24px",
  },
  header: {
    textAlign: "center",
    padding: "40px 0 24px",
  },
  title: {
    fontSize: "32px",
    fontWeight: "700",
    background: "linear-gradient(135deg, #60a5fa, #a78bfa)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    margin: "0 0 8px",
  },
  subtitle: {
    color: "#94a3b8",
    fontSize: "15px",
    margin: 0,
  },
  card: {
    background: "#111827",
    borderRadius: "16px",
    border: "1px solid #1e293b",
    padding: "32px",
    marginBottom: "20px",
  },
  label: {
    display: "block",
    fontSize: "13px",
    fontWeight: "600",
    color: "#94a3b8",
    marginBottom: "8px",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },
  select: {
    width: "100%",
    padding: "12px 16px",
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "10px",
    color: "#e2e8f0",
    fontSize: "15px",
    outline: "none",
    cursor: "pointer",
    marginBottom: "20px",
    appearance: "none",
  },
  grid2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "16px",
  },
  grid3: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr 1fr",
    gap: "12px",
    marginBottom: "20px",
  },
  diffBtn: (active) => ({
    padding: "14px",
    background: active ? "#3b82f6" : "#1e293b",
    border: active ? "1px solid #60a5fa" : "1px solid #334155",
    borderRadius: "10px",
    color: active ? "#fff" : "#94a3b8",
    fontSize: "14px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "all 0.2s",
    textTransform: "capitalize",
  }),
  primaryBtn: {
    width: "100%",
    padding: "16px",
    background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
    border: "none",
    borderRadius: "12px",
    color: "#fff",
    fontSize: "16px",
    fontWeight: "700",
    cursor: "pointer",
    transition: "opacity 0.2s",
    marginTop: "8px",
  },
  secondaryBtn: {
    padding: "12px 24px",
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "10px",
    color: "#e2e8f0",
    fontSize: "14px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  progressBar: {
    width: "100%",
    height: "6px",
    background: "#1e293b",
    borderRadius: "3px",
    marginBottom: "24px",
    overflow: "hidden",
  },
  progressFill: (pct) => ({
    width: `${pct}%`,
    height: "100%",
    background: "linear-gradient(90deg, #3b82f6, #8b5cf6)",
    borderRadius: "3px",
    transition: "width 0.5s ease",
  }),
  questionBox: {
    background: "#1e293b",
    borderLeft: "4px solid #3b82f6",
    borderRadius: "0 12px 12px 0",
    padding: "24px",
    marginBottom: "24px",
  },
  textarea: {
    width: "100%",
    minHeight: "160px",
    padding: "16px",
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "12px",
    color: "#e2e8f0",
    fontSize: "15px",
    lineHeight: "1.6",
    outline: "none",
    resize: "vertical",
    fontFamily: "inherit",
    marginBottom: "16px",
    boxSizing: "border-box",
  },
  scoreCard: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "12px",
    marginBottom: "20px",
  },
  scoreItem: (score) => ({
    background: score >= 8 ? "#064e3b" : score >= 5 ? "#713f12" : "#7f1d1d",
    border: `1px solid ${score >= 8 ? "#10b981" : score >= 5 ? "#f59e0b" : "#ef4444"}`,
    borderRadius: "12px",
    padding: "16px",
    textAlign: "center",
  }),
  scoreValue: {
    fontSize: "24px",
    fontWeight: "700",
    margin: "0 0 4px",
  },
  scoreLabel: {
    fontSize: "11px",
    color: "#94a3b8",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    margin: 0,
  },
  feedbackBox: {
    background: "#1e293b",
    borderRadius: "12px",
    padding: "20px",
    marginBottom: "16px",
  },
  improvedBox: {
    background: "#0c1a0e",
    border: "1px solid #166534",
    borderRadius: "12px",
    padding: "20px",
    marginBottom: "20px",
  },
  tag: {
    display: "inline-block",
    padding: "4px 10px",
    background: "#1e293b",
    borderRadius: "6px",
    fontSize: "12px",
    color: "#94a3b8",
    marginRight: "8px",
    marginBottom: "8px",
  },
  overallScore: (score) => ({
    fontSize: "48px",
    fontWeight: "800",
    color: score >= 8 ? "#10b981" : score >= 5 ? "#f59e0b" : "#ef4444",
    textAlign: "center",
    margin: "16px 0",
  }),
  resultRow: {
    background: "#1e293b",
    borderRadius: "12px",
    padding: "20px",
    marginBottom: "12px",
    cursor: "pointer",
    transition: "border-color 0.2s",
    border: "1px solid #334155",
  },
  spinner: {
    display: "inline-block",
    width: "20px",
    height: "20px",
    border: "2px solid #334155",
    borderTop: "2px solid #3b82f6",
    borderRadius: "50%",
    animation: "spin 0.8s linear infinite",
    marginRight: "8px",
    verticalAlign: "middle",
  },
  badge: (color) => ({
    display: "inline-block",
    padding: "4px 12px",
    borderRadius: "20px",
    fontSize: "12px",
    fontWeight: "600",
    background: color === "blue" ? "#1e3a5f" : color === "green" ? "#064e3b" : "#713f12",
    color: color === "blue" ? "#60a5fa" : color === "green" ? "#10b981" : "#f59e0b",
  }),
  backBtn: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    background: "none",
    border: "none",
    color: "#94a3b8",
    fontSize: "14px",
    cursor: "pointer",
    padding: "8px 0",
    marginBottom: "16px",
  },
};

// ── Spinner CSS (injected once) ─────────────────────────────────
const SpinnerStyle = () => (
  <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
);

// ── Setup Screen ────────────────────────────────────────────────
function SetupScreen({ onStart, connected }) {
  const [role, setRole] = useState("Software Engineer");
  const [topic, setTopic] = useState("Technical");
  const [difficulty, setDifficulty] = useState("Medium");
  const [numQuestions, setNumQuestions] = useState(5);
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/options`)
      .then((r) => r.json())
      .then((data) => {
        if (data.topics && data.topics[role]) {
          setTopics(data.topics[role]);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetch(`${API_BASE}/options`)
      .then((r) => r.json())
      .then((data) => {
        if (data.topics && data.topics[role]) {
          setTopics(data.topics[role]);
          setTopic(data.topics[role][0] || "Technical");
        }
      })
      .catch(() => {});
  }, [role]);

  const roles = [
    "Software Engineer", "Frontend Developer", "Backend Developer",
    "Data Scientist", "Data Analyst", "Product Manager",
    "DevOps Engineer", "Mobile App Developer", "UI/UX Designer", "QA/Test Engineer",
  ];

  return (
    <div>
      <div style={styles.header}>
        <h1 style={styles.title}>AI Mock Interview</h1>
        <p style={styles.subtitle}>Practice with your fine-tuned AI interviewer</p>
        <div style={{ marginTop: "12px" }}>
          <span style={styles.badge(connected ? "green" : "blue")}>
            {connected ? "Model Connected" : "Connecting..."}
          </span>
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.grid2}>
          <div>
            <label style={styles.label}>Job Role</label>
            <select style={styles.select} value={role} onChange={(e) => setRole(e.target.value)}>
              {roles.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label style={styles.label}>Topic</label>
            <select style={styles.select} value={topic} onChange={(e) => setTopic(e.target.value)}>
              {topics.length > 0
                ? topics.map((t) => <option key={t} value={t}>{t}</option>)
                : <option value="Technical">Technical</option>
              }
            </select>
          </div>
        </div>

        <label style={styles.label}>Difficulty</label>
        <div style={styles.grid3}>
          {["Easy", "Medium", "Hard"].map((d) => (
            <button key={d} style={styles.diffBtn(difficulty === d)} onClick={() => setDifficulty(d)}>
              {d}
            </button>
          ))}
        </div>

        <label style={styles.label}>Number of Questions</label>
        <div style={styles.grid3}>
          {[3, 5, 10].map((n) => (
            <button key={n} style={styles.diffBtn(numQuestions === n)} onClick={() => setNumQuestions(n)}>
              {n} Questions
            </button>
          ))}
        </div>

        <button
          style={{ ...styles.primaryBtn, opacity: connected ? 1 : 0.5 }}
          disabled={!connected}
          onClick={() => onStart(role, topic, difficulty, numQuestions)}
        >
          Start Interview
        </button>
      </div>
    </div>
  );
}

// ── Interview Screen ────────────────────────────────────────────
function InterviewScreen({ session, onComplete, onBack }) {
  const [currentQ, setCurrentQ] = useState(session.question);
  const [skills, setSkills] = useState(session.expected_skills || []);
  const [qNum, setQNum] = useState(1);
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [difficulty, setDifficulty] = useState(session.difficulty);
  const [allResults, setAllResults] = useState([]);
  const textareaRef = useRef(null);

  const totalQ = session.num_questions;
  const progress = ((qNum - 1) / totalQ) * 100;

  const submitAnswer = async () => {
    if (!answer.trim()) return;
    setLoading(true);
    setEvaluation(null);

    try {
      const r = await fetch(`${API_BASE}/api/interview/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: session.session_id, answer }),
      });
      const data = await r.json();

      const evalData = data.evaluation;
      setEvaluation(evalData);
      setAllResults((prev) => [...prev, { question: currentQ, answer, evaluation: evalData }]);

      if (data.status === "completed") {
        setTimeout(() => onComplete(session.session_id), 100);
      } else {
        setCurrentQ(data.next_question);
        setSkills(data.expected_skills || []);
        setQNum(data.question_number);
        setDifficulty(data.difficulty);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const nextQuestion = () => {
    setAnswer("");
    setEvaluation(null);
    if (textareaRef.current) textareaRef.current.focus();
  };

  return (
    <div>
      <button style={styles.backBtn} onClick={onBack}>
        ← Back to Setup
      </button>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div>
          <span style={styles.badge("blue")}>{session.role}</span>
          <span style={{ ...styles.badge("green"), marginLeft: "8px" }}>{difficulty}</span>
        </div>
        <span style={{ color: "#94a3b8", fontSize: "14px" }}>
          Question {qNum} of {totalQ}
        </span>
      </div>

      <div style={styles.progressBar}>
        <div style={styles.progressFill(progress)} />
      </div>

      {/* Question */}
      <div style={styles.questionBox}>
        <p style={{ margin: 0, fontSize: "18px", lineHeight: "1.6", fontWeight: "500" }}>{currentQ}</p>
        {skills.length > 0 && (
          <div style={{ marginTop: "12px" }}>
            {skills.map((s, i) => <span key={i} style={styles.tag}>{s}</span>)}
          </div>
        )}
      </div>

      {/* Answer or Evaluation */}
      {!evaluation ? (
        <div>
          <textarea
            ref={textareaRef}
            style={styles.textarea}
            placeholder="Type your answer here..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={loading}
          />
          <button
            style={{ ...styles.primaryBtn, opacity: loading || !answer.trim() ? 0.5 : 1 }}
            disabled={loading || !answer.trim()}
            onClick={submitAnswer}
          >
            {loading ? <><span style={styles.spinner} /> Evaluating...</> : "Submit Answer"}
          </button>
        </div>
      ) : (
        <div>
          {/* Scores */}
          <div style={styles.scoreCard}>
            {["clarity", "correctness", "relevance", "depth"].map((key) => {
              const val = evaluation.scores?.[key] || 0;
              return (
                <div key={key} style={styles.scoreItem(val)}>
                  <p style={styles.scoreValue}>{val}</p>
                  <p style={styles.scoreLabel}>{key}</p>
                </div>
              );
            })}
          </div>

          <div style={{ textAlign: "center", marginBottom: "20px" }}>
            <span style={{ fontSize: "14px", color: "#94a3b8" }}>Overall: </span>
            <span style={{ fontSize: "28px", fontWeight: "700", color: evaluation.overall >= 7 ? "#10b981" : evaluation.overall >= 5 ? "#f59e0b" : "#ef4444" }}>
              {evaluation.overall}/10
            </span>
          </div>

          {/* Feedback */}
          <div style={styles.feedbackBox}>
            <p style={{ margin: 0, fontSize: "14px", color: "#94a3b8", fontWeight: "600", marginBottom: "8px" }}>FEEDBACK</p>
            <p style={{ margin: 0, fontSize: "15px", lineHeight: "1.6" }}>{evaluation.feedback}</p>
          </div>

          {/* Improved Answer */}
          {evaluation.improved_answer && (
            <div style={styles.improvedBox}>
              <p style={{ margin: 0, fontSize: "14px", color: "#10b981", fontWeight: "600", marginBottom: "8px" }}>STRONGER ANSWER</p>
              <p style={{ margin: 0, fontSize: "15px", lineHeight: "1.6", color: "#d1fae5" }}>{evaluation.improved_answer}</p>
            </div>
          )}

          <button style={styles.primaryBtn} onClick={nextQuestion}>
            {qNum >= totalQ ? "View Results" : "Next Question →"}
          </button>
        </div>
      )}
    </div>
  );
}

// ── Results Screen ──────────────────────────────────────────────
function ResultsScreen({ sessionId, onRestart }) {
  const [summary, setSummary] = useState(null);
  const [expandedQ, setExpandedQ] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/interview/summary/${sessionId}`)
      .then((r) => r.json())
      .then(setSummary)
      .catch(console.error);
  }, [sessionId]);

  if (!summary) return <p style={{ textAlign: "center", color: "#94a3b8" }}>Loading results...</p>;

  const results = summary.results || [];
  const avg = summary.average_overall || 0;

  return (
    <div>
      <div style={{ ...styles.card, textAlign: "center" }}>
        <p style={{ ...styles.label, marginBottom: "4px" }}>Interview Complete</p>
        <h2 style={{ margin: "0 0 8px", fontSize: "20px" }}>{summary.role} — {summary.topic}</h2>
        <div style={styles.overallScore(avg)}>{avg}/10</div>

        <div style={styles.scoreCard}>
          {Object.entries(summary.average_scores || {}).map(([key, val]) => (
            <div key={key} style={styles.scoreItem(val)}>
              <p style={styles.scoreValue}>{val}</p>
              <p style={styles.scoreLabel}>{key}</p>
            </div>
          ))}
        </div>

        <div style={{ display: "flex", gap: "12px", justifyContent: "center", marginTop: "8px" }}>
          <span style={styles.badge("green")}>Best: {summary.strongest_area}</span>
          <span style={styles.badge("blue")}>Improve: {summary.weakest_area}</span>
        </div>
      </div>

      <h3 style={{ fontSize: "16px", fontWeight: "600", marginBottom: "12px" }}>Question Breakdown</h3>

      {results.map((r, i) => (
        <div
          key={i}
          style={{ ...styles.resultRow, borderColor: expandedQ === i ? "#3b82f6" : "#334155" }}
          onClick={() => setExpandedQ(expandedQ === i ? null : i)}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontWeight: "600", fontSize: "14px" }}>Q{r.question_number}: {r.question?.substring(0, 60)}...</span>
            <span style={{ fontWeight: "700", color: r.overall >= 7 ? "#10b981" : r.overall >= 5 ? "#f59e0b" : "#ef4444" }}>
              {r.overall}/10
            </span>
          </div>

          {expandedQ === i && (
            <div style={{ marginTop: "16px", fontSize: "14px" }}>
              <p style={{ color: "#94a3b8", marginBottom: "4px" }}>Your answer:</p>
              <p style={{ marginBottom: "12px", lineHeight: "1.5" }}>{r.answer}</p>
              <p style={{ color: "#94a3b8", marginBottom: "4px" }}>Feedback:</p>
              <p style={{ marginBottom: "12px", lineHeight: "1.5" }}>{r.feedback}</p>
              {r.improved_answer && (
                <>
                  <p style={{ color: "#10b981", marginBottom: "4px" }}>Stronger answer:</p>
                  <p style={{ lineHeight: "1.5", color: "#d1fae5" }}>{r.improved_answer}</p>
                </>
              )}
            </div>
          )}
        </div>
      ))}

      <button style={{ ...styles.primaryBtn, marginTop: "20px" }} onClick={onRestart}>
        Start New Interview
      </button>
    </div>
  );
}

// ── Main App ────────────────────────────────────────────────────
export default function MockInterview() {
  const [screen, setScreen] = useState("setup");
  const [session, setSession] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => r.json())
      .then((data) => setConnected(data.model_server === "connected"))
      .catch(() => setConnected(false));
  }, []);

  const handleStart = async (role, topic, difficulty, numQuestions) => {
    try {
      const r = await fetch(`${API_BASE}/api/interview/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role, topic, difficulty, num_questions: numQuestions }),
      });
      const data = await r.json();
      setSession({ ...data, role, topic, difficulty, num_questions: numQuestions });
      setScreen("interview");
    } catch (e) {
      console.error(e);
    }
  };

  const handleComplete = (sid) => {
    setSessionId(sid);
    setScreen("results");
  };

  const handleRestart = () => {
    setSession(null);
    setSessionId(null);
    setScreen("setup");
  };

  return (
    <div style={styles.page}>
      <SpinnerStyle />
      <div style={styles.container}>
        {screen === "setup" && (
          <SetupScreen onStart={handleStart} connected={connected} />
        )}
        {screen === "interview" && session && (
          <InterviewScreen
            session={session}
            onComplete={handleComplete}
            onBack={handleRestart}
          />
        )}
        {screen === "results" && sessionId && (
          <ResultsScreen sessionId={sessionId} onRestart={handleRestart} />
        )}
      </div>
    </div>
  );
}
