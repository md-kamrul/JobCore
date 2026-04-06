import React, { useState, useRef } from "react";

/* ─── shared input styles ─── */
const inp = {
  width: "100%", background: "#0f172a", border: "1px solid #334155",
  borderRadius: "8px", padding: "8px 12px", color: "#e2e8f0",
  fontSize: "14px", outline: "none", boxSizing: "border-box",
};
const TA = (props) => (
  <textarea {...props} style={{ ...inp, resize: "vertical", ...props.style }} />
);
const IN = (props) => <input {...props} style={{ ...inp, ...props.style }} />;

/* ─── reusable field ─── */
const Field = ({ label, value, editing, onChange, type = "text", multiline }) => (
  <div style={{ marginBottom: "14px" }}>
    <p style={{ color: "#94a3b8", fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "6px" }}>
      {label}
    </p>
    {editing ? (
      multiline
        ? <TA rows={3} value={value} onChange={(e) => onChange(e.target.value)} />
        : <IN type={type} value={value} onChange={(e) => onChange(e.target.value)} />
    ) : (
      <div style={{ background: "#0f172a", borderRadius: "8px", padding: "8px 12px", color: "#e2e8f0", fontSize: "14px" }}>
        {value || <span style={{ color: "#475569" }}>Not set</span>}
      </div>
    )}
  </div>
);

/* ─── edit action buttons ─── */
const EditBar = ({ editing, onEdit, onSave, onCancel }) => (
  <div style={{ display: "flex", gap: "8px" }}>
    {editing ? (
      <>
        <button onClick={onSave} style={{ background: "#15803d", color: "white", border: "none", borderRadius: "8px", padding: "7px 16px", fontSize: "12px", fontWeight: 600, cursor: "pointer" }}>✓ Save</button>
        <button onClick={onCancel} style={{ background: "#334155", color: "#cbd5e1", border: "none", borderRadius: "8px", padding: "7px 16px", fontSize: "12px", fontWeight: 600, cursor: "pointer" }}>✕ Cancel</button>
      </>
    ) : (
      <button onClick={onEdit} style={{ background: "#1d4ed8", color: "white", border: "none", borderRadius: "8px", padding: "7px 16px", fontSize: "12px", fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: "6px" }}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="white"><path d="M3 17.25V21h3.75l11-11.03-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 000-1.41l-2.34-2.34a1 1 0 00-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" /></svg>
        Edit
      </button>
    )}
  </div>
);

/* ─── helpers ─── */
function formatBytes(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

/* ─── CV / Resume sub-section ─── */
const CVSection = () => {
  const cvInputRef = useRef(null);
  const [cvFile, setCvFile] = useState(null);
  const [cvDataUrl, setCvDataUrl] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [cvNote, setCvNote] = useState("");
  const [editingNote, setEditingNote] = useState(false);
  const [noteDraft, setNoteDraft] = useState("");

  const handleCvFile = (file) => {
    if (!file) return;
    const allowed = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    if (!allowed.includes(file.type) && !file.name.match(/\.(pdf|doc|docx)$/i)) {
      alert("Please upload a PDF or Word document.");
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => setCvDataUrl(e.target.result);
    reader.readAsDataURL(file);
    setCvFile({
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date().toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }),
    });
  };

  const isPdf = cvFile && (cvFile.type === "application/pdf" || cvFile.name.endsWith(".pdf"));

  const iconForType = (f) => {
    if (!f) return null;
    if (f.type === "application/pdf" || f.name.endsWith(".pdf"))
      return (
        <svg width="28" height="28" viewBox="0 0 24 24" fill="#ef4444">
          <path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM13 13h1V8.5h-1V13z" />
        </svg>
      );
    return (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="#3b82f6">
        <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.89 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 7V3.5L18.5 9H13z" />
      </svg>
    );
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="#60a5fa">
            <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.89 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 7V3.5L18.5 9H13z" />
          </svg>
          <h3 style={{ fontSize: "14px", fontWeight: 700, color: "#f1f5f9", margin: 0 }}>CV / Resume</h3>
        </div>
        {cvFile && (
          <button
            onClick={() => { setCvFile(null); setCvDataUrl(null); setCvNote(""); }}
            style={{ background: "#450a0a", color: "#f87171", border: "1px solid #7f1d1d", borderRadius: "6px", padding: "4px 10px", fontSize: "11px", cursor: "pointer" }}
          >
            ✕ Remove
          </button>
        )}
      </div>

      {!cvFile ? (
        <div
          className={`cv-drop${dragging ? " drag" : ""}`}
          onClick={() => cvInputRef.current.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); handleCvFile(e.dataTransfer.files[0]); }}
          style={{ border: "2px dashed #334155", borderRadius: "12px", padding: "28px 20px", textAlign: "center", cursor: "pointer", transition: "all 0.2s", background: "#0f172a" }}
        >
          <input
            ref={cvInputRef}
            type="file"
            accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            style={{ display: "none" }}
            onChange={(e) => handleCvFile(e.target.files[0])}
          />
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "10px", pointerEvents: "none" }}>
            <div style={{ width: "44px", height: "44px", borderRadius: "10px", background: "#1e3a5f", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="#60a5fa">
                <path d="M19.35 10.04A7.49 7.49 0 0012 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 000 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z" />
              </svg>
            </div>
            <div>
              <p style={{ color: "#e2e8f0", fontSize: "13px", fontWeight: 600, marginBottom: "3px" }}>Drop your CV here or click to browse</p>
              <p style={{ color: "#475569", fontSize: "11px" }}>PDF, DOC, DOCX — max 10 MB</p>
            </div>
          </div>
        </div>
      ) : (
        <div>
          {/* File info row */}
          <div style={{ background: "#0f172a", borderRadius: "12px", border: "1px solid #1e3a5f", padding: "14px", display: "flex", gap: "14px", alignItems: "center", marginBottom: "12px" }}>
            <div style={{ width: "48px", height: "48px", borderRadius: "10px", background: "#1e293b", border: "1px solid #334155", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              {iconForType(cvFile)}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ fontWeight: 600, fontSize: "13px", color: "#f1f5f9", margin: "0 0 3px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{cvFile.name}</p>
              <p style={{ fontSize: "11px", color: "#64748b", margin: 0 }}>{formatBytes(cvFile.size)} · Uploaded {cvFile.uploadedAt}</p>
            </div>
            <div style={{ display: "flex", gap: "8px", flexShrink: 0 }}>
              {isPdf && cvDataUrl && (
                <a href={cvDataUrl} target="_blank" rel="noreferrer" style={{ display: "flex", alignItems: "center", gap: "5px", background: "#1e3a5f", color: "#60a5fa", border: "1px solid #2563eb44", borderRadius: "7px", padding: "5px 10px", fontSize: "11px", fontWeight: 600, textDecoration: "none" }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="#60a5fa"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" /></svg>
                  View
                </a>
              )}
              {cvDataUrl && (
                <a href={cvDataUrl} download={cvFile.name} style={{ display: "flex", alignItems: "center", gap: "5px", background: "#052e16", color: "#4ade80", border: "1px solid #14532d44", borderRadius: "7px", padding: "5px 10px", fontSize: "11px", fontWeight: 600, textDecoration: "none" }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="#4ade80"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" /></svg>
                  Download
                </a>
              )}
            </div>
          </div>

          {/* Note row */}
          <div style={{ background: "#0f172a", borderRadius: "10px", border: "1px solid #1e3a5f", padding: "12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
              <p style={{ color: "#94a3b8", fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.08em", margin: 0 }}>Note</p>
              {editingNote ? (
                <div style={{ display: "flex", gap: "6px" }}>
                  <button onClick={() => { setCvNote(noteDraft); setEditingNote(false); }} style={{ background: "#15803d", color: "white", border: "none", borderRadius: "6px", padding: "4px 10px", fontSize: "11px", cursor: "pointer" }}>✓ Save</button>
                  <button onClick={() => setEditingNote(false)} style={{ background: "#334155", color: "#cbd5e1", border: "none", borderRadius: "6px", padding: "4px 10px", fontSize: "11px", cursor: "pointer" }}>✕</button>
                </div>
              ) : (
                <button onClick={() => { setNoteDraft(cvNote); setEditingNote(true); }} style={{ background: "transparent", color: "#60a5fa", border: "none", fontSize: "11px", cursor: "pointer", padding: 0 }}>
                  {cvNote ? "Edit note" : "+ Add note"}
                </button>
              )}
            </div>
            {editingNote
              ? <TA rows={2} value={noteDraft} placeholder="e.g. Latest version — updated April 2026" onChange={(e) => setNoteDraft(e.target.value)} />
              : <p style={{ color: cvNote ? "#cbd5e1" : "#334155", fontSize: "12px", margin: 0, fontStyle: cvNote ? "normal" : "italic" }}>{cvNote || "No note added."}</p>
            }
          </div>
        </div>
      )}
    </div>
  );
};

const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899"];

const ProfileSection = () => {
  const fileInputRef = useRef(null);
  const [profileImage, setProfileImage] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const [profile, setProfile] = useState({
    name: "Farhan Ishraque", email: "farhan.ishraque@email.com",
    bio: "Passionate product designer with a knack for creating intuitive and delightful user experiences.",
    desiredRole: "Product Designer",
  });
  const [profileDraft, setProfileDraft] = useState({ ...profile });
  const [editingProfile, setEditingProfile] = useState(false);

  const [contact, setContact] = useState({
    email: "farhan.ishraque@email.com", phone: "+1 (415) 000-0000",
    website: "farhanishraque.design", linkedin: "linkedin.com/in/farhanishraque",
  });
  const [contactDraft, setContactDraft] = useState({ ...contact });
  const [editingContact, setEditingContact] = useState(false);

  const [work, setWork] = useState([
    { id: 1, role: "Senior Product Designer", company: "TechCorp Inc.", period: "Jan 2022 – Present", description: "Led end-to-end product design for mobile & web platforms serving 2M+ users.", color: "#3b82f6" },
    { id: 2, role: "UX Designer", company: "CreativeMinds Studio", period: "Jun 2019 – Dec 2021", description: "Designed cohesive design systems and collaborated with cross-functional teams.", color: "#8b5cf6" },
  ]);
  const [workDraft, setWorkDraft] = useState(work.map(w => ({ ...w })));
  const [editingWork, setEditingWork] = useState(false);

  const [edu, setEdu] = useState([
    { id: 1, degree: "B.Sc. in Human-Computer Interaction", school: "UC Berkeley", period: "2015 – 2019", gpa: "3.8 / 4.0", color: "#f59e0b" },
  ]);
  const [eduDraft, setEduDraft] = useState(edu.map(e => ({ ...e })));
  const [editingEdu, setEditingEdu] = useState(false);

  const handleImageUpload = (e) => {
    const file = e.target.files[0]; if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setProfileImage(reader.result);
    reader.readAsDataURL(file);
  };

  const updateWorkDraft = (id, field, val) =>
    setWorkDraft(prev => prev.map(w => w.id === id ? { ...w, [field]: val } : w));
  const updateEduDraft = (id, field, val) =>
    setEduDraft(prev => prev.map(e => e.id === id ? { ...e, [field]: val } : e));
  const addWork = () => setWorkDraft(prev => [...prev, { id: Date.now(), role: "", company: "", period: "", description: "", color: COLORS[prev.length % COLORS.length] }]);
  const removeWork = (id) => setWorkDraft(prev => prev.filter(w => w.id !== id));
  const addEdu = () => setEduDraft(prev => [...prev, { id: Date.now(), degree: "", school: "", period: "", gpa: "", color: COLORS[(prev.length + 2) % COLORS.length] }]);
  const removeEdu = (id) => setEduDraft(prev => prev.filter(e => e.id !== id));

  const cardStyle = { background: "#1e293b", borderRadius: "16px", padding: "24px", border: "1px solid #1e3a5f", marginBottom: "18px" };
  const sectionHead = { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" };
  const h3Style = { fontSize: "15px", fontWeight: 700, color: "#f1f5f9", margin: 0 };
  const labelStyle = { color: "#94a3b8", fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "6px" };

  const tabs = [
    { key: "overview", label: "Overview" },
    { key: "work", label: "Work & Education" },
    { key: "contact", label: "Contact & Info" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg,#0a0f1e 0%,#0d1829 50%,#091424 100%)", fontFamily: "'DM Sans','Segoe UI',sans-serif", color: "#e2e8f0", padding: "28px 20px" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
        input:focus,textarea:focus{border-color:#3b82f6!important;box-shadow:0 0 0 3px rgba(59,130,246,0.15)!important;outline:none}
        .av-wrap:hover .av-ov{opacity:1!important}
        button:active{opacity:0.85}
        .rm-btn:hover{background:#7f1d1d!important;color:#fca5a5!important}
        .cv-drop{border:2px dashed #334155;border-radius:12px;padding:28px 20px;text-align:center;cursor:pointer;transition:all 0.2s;background:#0f172a;}
        .cv-drop:hover,.cv-drop.drag{border-color:#3b82f6;}
      `}</style>

      <div style={{ maxWidth: "1080px", margin: "0 auto" }}>

        {/* ── HEADER ── */}
        <div style={{ background: "linear-gradient(135deg,#1e293b,#162032)", borderRadius: "20px", padding: "28px", marginBottom: "20px", border: "1px solid #1e3a5f", display: "flex", alignItems: "center", gap: "22px", flexWrap: "wrap", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: 0, right: 0, width: "160px", height: "160px", background: "radial-gradient(circle,rgba(59,130,246,0.1) 0%,transparent 70%)", pointerEvents: "none" }} />
          <div className="av-wrap" style={{ position: "relative", cursor: "pointer", flexShrink: 0 }} onClick={() => fileInputRef.current.click()}>
            <div style={{ width: "96px", height: "96px", borderRadius: "50%", border: "3px solid #3b82f6", overflow: "hidden", background: "#0f172a", display: "flex", alignItems: "center", justifyContent: "center" }}>
              {profileImage
                ? <img src={profileImage} alt="profile" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                : <svg width="44" height="44" viewBox="0 0 24 24" fill="#475569"><path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z" /></svg>}
            </div>
            <div className="av-ov" style={{ position: "absolute", inset: 0, borderRadius: "50%", background: "rgba(0,0,0,0.58)", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: "3px", opacity: 0, transition: "opacity 0.2s" }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="white"><path d="M12 16l-4-4h2.5V8h3v4H16l-4 4zm-7 2h14v2H5v-2z" /></svg>
              <span style={{ color: "white", fontSize: "9px", fontWeight: 700 }}>UPLOAD</span>
            </div>
            <input ref={fileInputRef} type="file" accept="image/*" style={{ display: "none" }} onChange={handleImageUpload} />
          </div>
          <div style={{ flex: 1, minWidth: "200px" }}>
            {editingProfile ? (
              <>
                <IN value={profileDraft.name} onChange={e => setProfileDraft({ ...profileDraft, name: e.target.value })} style={{ fontSize: "20px", fontWeight: 700, marginBottom: "8px" }} />
                <TA value={profileDraft.bio} onChange={e => setProfileDraft({ ...profileDraft, bio: e.target.value })} rows={2} style={{ marginBottom: 0 }} />
              </>
            ) : (
              <>
                <h1 style={{ fontSize: "24px", fontWeight: 700, color: "#f1f5f9", margin: "0 0 3px" }}>{profile.name}</h1>
                <p style={{ color: "#60a5fa", fontSize: "13px", margin: "0 0 8px" }}>{profile.desiredRole}</p>
                <p style={{ color: "#94a3b8", fontSize: "13px", lineHeight: 1.6, margin: 0 }}>{profile.bio}</p>
              </>
            )}
          </div>
          <EditBar editing={editingProfile} onEdit={() => { setProfileDraft({ ...profile }); setEditingProfile(true); }} onSave={() => { setProfile({ ...profileDraft }); setEditingProfile(false); }} onCancel={() => setEditingProfile(false)} />
        </div>

        {/* ── TABS ── */}
        <div style={{ display: "flex", gap: "3px", background: "#0f172a", borderRadius: "10px", padding: "3px", width: "fit-content", marginBottom: "20px", flexWrap: "wrap" }}>
          {tabs.map(t => (
            <button key={t.key} onClick={() => setActiveTab(t.key)} style={{ padding: "7px 18px", borderRadius: "8px", border: "none", cursor: "pointer", fontSize: "12px", fontWeight: 500, background: activeTab === t.key ? "#1e40af" : "transparent", color: activeTab === t.key ? "white" : "#64748b", transition: "all 0.2s" }}>
              {t.label}
            </button>
          ))}
        </div>

        {/* ── LAYOUT ── */}
        <div style={{ display: "flex", gap: "20px", alignItems: "flex-start" }}>
          <div style={{ flex: 1, minWidth: "280px" }}>

            {/* ── OVERVIEW ── */}
            {activeTab === "overview" && (
              <div style={cardStyle}>
                <div style={sectionHead}>
                  <h3 style={h3Style}>Profile Overview</h3>
                  <EditBar editing={editingProfile} onEdit={() => { setProfileDraft({ ...profile }); setEditingProfile(true); }} onSave={() => { setProfile({ ...profileDraft }); setEditingProfile(false); }} onCancel={() => setEditingProfile(false)} />
                </div>
                <Field label="Full Name" value={editingProfile ? profileDraft.name : profile.name} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, name: v })} />
                <Field label="Email" value={editingProfile ? profileDraft.email : profile.email} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, email: v })} type="email" />
                <Field label="Bio" value={editingProfile ? profileDraft.bio : profile.bio} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, bio: v })} multiline />

                {/* ── CV SECTION ── */}
                <div style={{ borderTop: "1px solid #0f172a", marginTop: "6px", paddingTop: "20px" }}>
                  <CVSection />
                </div>
              </div>
            )}

            {/* ── WORK & EDUCATION ── */}
            {activeTab === "work" && (
              <>
                <div style={cardStyle}>
                  <div style={sectionHead}>
                    <h3 style={h3Style}>Work Experience</h3>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      {editingWork && <button onClick={addWork} style={{ background: "#1e3a5f", color: "#60a5fa", border: "1px solid #2563eb", borderRadius: "8px", padding: "6px 12px", fontSize: "11px", cursor: "pointer" }}>+ Add</button>}
                      <EditBar editing={editingWork} onEdit={() => { setWorkDraft(work.map(w => ({ ...w }))); setEditingWork(true); }} onSave={() => { setWork([...workDraft]); setEditingWork(false); }} onCancel={() => { setWorkDraft(work.map(w => ({ ...w }))); setEditingWork(false); }} />
                    </div>
                  </div>
                  {(editingWork ? workDraft : work).length === 0 && <p style={{ color: "#475569", fontSize: "13px", textAlign: "center", padding: "20px 0", margin: 0 }}>No entries. {editingWork ? 'Click "+ Add" to add one.' : ''}</p>}
                  {(editingWork ? workDraft : work).map((job, i, arr) => (
                    <div key={job.id} style={{ display: "flex", gap: "14px", paddingBottom: i < arr.length - 1 ? "18px" : 0, marginBottom: i < arr.length - 1 ? "18px" : 0, borderBottom: i < arr.length - 1 ? "1px solid #0f172a" : "none" }}>
                      <div style={{ width: "42px", height: "42px", borderRadius: "10px", background: job.color + "22", border: `1px solid ${job.color}44`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, color: job.color, fontWeight: 700, fontSize: "16px" }}>{(job.company || "?")[0].toUpperCase()}</div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        {editingWork ? (
                          <>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
                              <div><p style={labelStyle}>Role</p><IN value={job.role} placeholder="Job title" onChange={e => updateWorkDraft(job.id, "role", e.target.value)} /></div>
                              <div><p style={labelStyle}>Company</p><IN value={job.company} placeholder="Company name" onChange={e => updateWorkDraft(job.id, "company", e.target.value)} /></div>
                            </div>
                            <div style={{ marginBottom: "8px" }}><p style={labelStyle}>Period</p><IN value={job.period} placeholder="e.g. Jan 2022 – Present" onChange={e => updateWorkDraft(job.id, "period", e.target.value)} /></div>
                            <div style={{ marginBottom: "10px" }}><p style={labelStyle}>Description</p><TA rows={2} value={job.description} placeholder="Describe your role..." onChange={e => updateWorkDraft(job.id, "description", e.target.value)} /></div>
                            <button className="rm-btn" onClick={() => removeWork(job.id)} style={{ background: "#450a0a", color: "#f87171", border: "1px solid #7f1d1d", borderRadius: "6px", padding: "4px 10px", fontSize: "11px", cursor: "pointer", transition: "all 0.2s" }}>✕ Remove</button>
                          </>
                        ) : (
                          <>
                            <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "6px", marginBottom: "3px" }}>
                              <p style={{ fontWeight: 600, fontSize: "14px", color: "#f1f5f9", margin: 0 }}>{job.role}</p>
                              <span style={{ fontSize: "10px", color: "#60a5fa", background: "#1e3a5f", padding: "2px 8px", borderRadius: "20px" }}>{job.period}</span>
                            </div>
                            <p style={{ color: "#94a3b8", fontSize: "12px", margin: "0 0 4px" }}>{job.company}</p>
                            <p style={{ color: "#64748b", fontSize: "12px", lineHeight: 1.6, margin: 0 }}>{job.description}</p>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div style={cardStyle}>
                  <div style={sectionHead}>
                    <h3 style={h3Style}>Education</h3>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      {editingEdu && <button onClick={addEdu} style={{ background: "#1e3a5f", color: "#60a5fa", border: "1px solid #2563eb", borderRadius: "8px", padding: "6px 12px", fontSize: "11px", cursor: "pointer" }}>+ Add</button>}
                      <EditBar editing={editingEdu} onEdit={() => { setEduDraft(edu.map(e => ({ ...e }))); setEditingEdu(true); }} onSave={() => { setEdu([...eduDraft]); setEditingEdu(false); }} onCancel={() => { setEduDraft(edu.map(e => ({ ...e }))); setEditingEdu(false); }} />
                    </div>
                  </div>
                  {(editingEdu ? eduDraft : edu).length === 0 && <p style={{ color: "#475569", fontSize: "13px", textAlign: "center", padding: "20px 0", margin: 0 }}>No entries. {editingEdu ? 'Click "+ Add" to add one.' : ''}</p>}
                  {(editingEdu ? eduDraft : edu).map((e, i, arr) => (
                    <div key={e.id} style={{ display: "flex", gap: "14px", paddingBottom: i < arr.length - 1 ? "18px" : 0, marginBottom: i < arr.length - 1 ? "18px" : 0, borderBottom: i < arr.length - 1 ? "1px solid #0f172a" : "none" }}>
                      <div style={{ width: "42px", height: "42px", borderRadius: "10px", background: e.color + "22", border: `1px solid ${e.color}44`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, color: e.color, fontWeight: 700, fontSize: "16px" }}>{(e.school || "?")[0].toUpperCase()}</div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        {editingEdu ? (
                          <>
                            <div style={{ marginBottom: "8px" }}><p style={labelStyle}>Degree</p><IN value={e.degree} placeholder="Degree / qualification" onChange={ev => updateEduDraft(e.id, "degree", ev.target.value)} /></div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
                              <div><p style={labelStyle}>School</p><IN value={e.school} placeholder="Institution name" onChange={ev => updateEduDraft(e.id, "school", ev.target.value)} /></div>
                              <div><p style={labelStyle}>GPA</p><IN value={e.gpa} placeholder="e.g. 3.8 / 4.0" onChange={ev => updateEduDraft(e.id, "gpa", ev.target.value)} /></div>
                            </div>
                            <div style={{ marginBottom: "10px" }}><p style={labelStyle}>Period</p><IN value={e.period} placeholder="e.g. 2015 – 2019" onChange={ev => updateEduDraft(e.id, "period", ev.target.value)} /></div>
                            <button className="rm-btn" onClick={() => removeEdu(e.id)} style={{ background: "#450a0a", color: "#f87171", border: "1px solid #7f1d1d", borderRadius: "6px", padding: "4px 10px", fontSize: "11px", cursor: "pointer", transition: "all 0.2s" }}>✕ Remove</button>
                          </>
                        ) : (
                          <>
                            <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "6px", marginBottom: "3px" }}>
                              <p style={{ fontWeight: 600, fontSize: "14px", color: "#f1f5f9", margin: 0 }}>{e.degree}</p>
                              <span style={{ fontSize: "10px", color: "#f59e0b", background: "#78350f33", padding: "2px 8px", borderRadius: "20px" }}>{e.period}</span>
                            </div>
                            <p style={{ color: "#94a3b8", fontSize: "12px", margin: "0 0 3px" }}>{e.school}</p>
                            <p style={{ color: "#64748b", fontSize: "12px", margin: 0 }}>GPA: {e.gpa}</p>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* ── CONTACT ── */}
            {activeTab === "contact" && (
              <div style={cardStyle}>
                <div style={sectionHead}>
                  <h3 style={h3Style}>Contact & Basic Info</h3>
                  <EditBar editing={editingContact} onEdit={() => { setContactDraft({ ...contact }); setEditingContact(true); }} onSave={() => { setContact({ ...contactDraft }); setEditingContact(false); }} onCancel={() => setEditingContact(false)} />
                </div>
                <Field label="Email Address" value={editingContact ? contactDraft.email : contact.email} editing={editingContact} onChange={v => setContactDraft({ ...contactDraft, email: v })} type="email" />
                <Field label="Phone Number" value={editingContact ? contactDraft.phone : contact.phone} editing={editingContact} onChange={v => setContactDraft({ ...contactDraft, phone: v })} type="tel" />
                <Field label="Website / Portfolio" value={editingContact ? contactDraft.website : contact.website} editing={editingContact} onChange={v => setContactDraft({ ...contactDraft, website: v })} />
                <Field label="LinkedIn" value={editingContact ? contactDraft.linkedin : contact.linkedin} editing={editingContact} onChange={v => setContactDraft({ ...contactDraft, linkedin: v })} />
                <div style={{ marginTop: "16px", padding: "14px", background: "#0f172a", borderRadius: "12px", border: "1px solid #1e3a5f" }}>
                  <p style={{ color: "#94a3b8", fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "10px" }}>Quick Links</p>
                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                    {[["🌐", "Portfolio", contact.website], ["💼", "LinkedIn", contact.linkedin], ["✉️", "Email", `mailto:${contact.email}`]].map(([ic, lb, href], i) => (
                      <a key={i} href={i === 2 ? href : `https://${href}`} style={{ display: "flex", alignItems: "center", gap: "6px", background: "#1e293b", border: "1px solid #334155", borderRadius: "7px", padding: "5px 10px", color: "#94a3b8", fontSize: "11px", textDecoration: "none" }}>
                        {ic} {lb}
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileSection;