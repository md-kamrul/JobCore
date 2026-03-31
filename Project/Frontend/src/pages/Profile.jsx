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

const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899"];

const ProfileSection = () => {
  const fileInputRef = useRef(null);
  const [profileImage, setProfileImage] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  /* ── profile (overview + header) ── */
  const [profile, setProfile] = useState({
    name: "Farhan Ishraque", email: "farhan.ishraque@email.com",
    bio: "Passionate product designer with a knack for creating intuitive and delightful user experiences.",
    desiredRole: "Product Designer", location: "Remote, San Francisco",
    salary: "$120,000 - $150,000", openToWork: true,
  });
  const [profileDraft, setProfileDraft] = useState({ ...profile });
  const [editingProfile, setEditingProfile] = useState(false);

  /* ── contact ── */
  const [contact, setContact] = useState({
    email: "farhan.ishraque@email.com", phone: "+1 (415) 000-0000",
    website: "farhanishraque.design", linkedin: "linkedin.com/in/farhanishraque",
  });
  const [contactDraft, setContactDraft] = useState({ ...contact });
  const [editingContact, setEditingContact] = useState(false);

  /* ── location ── */
  const [location, setLocation] = useState({
    city: "San Francisco", state: "California", country: "United States", workPref: "Remote",
  });
  const [locationDraft, setLocationDraft] = useState({ ...location });
  const [editingLocation, setEditingLocation] = useState(false);

  /* ── work experience ── */
  const [work, setWork] = useState([
    { id: 1, role: "Senior Product Designer", company: "TechCorp Inc.", period: "Jan 2022 – Present", description: "Led end-to-end product design for mobile & web platforms serving 2M+ users.", color: "#3b82f6" },
    { id: 2, role: "UX Designer", company: "CreativeMinds Studio", period: "Jun 2019 – Dec 2021", description: "Designed cohesive design systems and collaborated with cross-functional teams.", color: "#8b5cf6" },
  ]);
  const [workDraft, setWorkDraft] = useState(work.map(w => ({ ...w })));
  const [editingWork, setEditingWork] = useState(false);

  /* ── education ── */
  const [edu, setEdu] = useState([
    { id: 1, degree: "B.Sc. in Human-Computer Interaction", school: "UC Berkeley", period: "2015 – 2019", gpa: "3.8 / 4.0", color: "#f59e0b" },
  ]);
  const [eduDraft, setEduDraft] = useState(edu.map(e => ({ ...e })));
  const [editingEdu, setEditingEdu] = useState(false);

  /* ── helpers ── */
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

  const addWork = () => {
    const newItem = { id: Date.now(), role: "", company: "", period: "", description: "", color: COLORS[workDraft.length % COLORS.length] };
    setWorkDraft(prev => [...prev, newItem]);
  };

  const removeWork = (id) => setWorkDraft(prev => prev.filter(w => w.id !== id));

  const addEdu = () => {
    const newItem = { id: Date.now(), degree: "", school: "", period: "", gpa: "", color: COLORS[(eduDraft.length + 2) % COLORS.length] };
    setEduDraft(prev => [...prev, newItem]);
  };

  const removeEdu = (id) => setEduDraft(prev => prev.filter(e => e.id !== id));

  const cardStyle = { background: "#1e293b", borderRadius: "16px", padding: "24px", border: "1px solid #1e3a5f", marginBottom: "18px" };
  const sectionHead = { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" };
  const h3Style = { fontSize: "15px", fontWeight: 700, color: "#f1f5f9", margin: 0 };
  const labelStyle = { color: "#94a3b8", fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "6px" };

  const tabs = [
    { key: "overview", label: "Overview" },
    { key: "work", label: "Work & Education" },
    { key: "contact", label: "Contact & Info" },
    { key: "location", label: "Location" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg,#0a0f1e 0%,#0d1829 50%,#091424 100%)", fontFamily: "'DM Sans','Segoe UI',sans-serif", color: "#e2e8f0", padding: "28px 20px" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
        input:focus,textarea:focus{border-color:#3b82f6!important;box-shadow:0 0 0 3px rgba(59,130,246,0.15)!important;outline:none}
        .av-wrap:hover .av-ov{opacity:1!important}
        button:active{opacity:0.85}
        .rm-btn:hover{background:#7f1d1d!important;color:#fca5a5!important}
      `}</style>

      <div style={{ maxWidth: "1080px", margin: "0 auto" }}>

        {/* ── HEADER ── */}
        <div style={{ background: "linear-gradient(135deg,#1e293b,#162032)", borderRadius: "20px", padding: "28px", marginBottom: "20px", border: "1px solid #1e3a5f", display: "flex", alignItems: "center", gap: "22px", flexWrap: "wrap", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", top: 0, right: 0, width: "160px", height: "160px", background: "radial-gradient(circle,rgba(59,130,246,0.1) 0%,transparent 70%)", pointerEvents: "none" }} />

          {/* avatar */}
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

          {/* name / bio */}
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

          <EditBar
            editing={editingProfile}
            onEdit={() => { setProfileDraft({ ...profile }); setEditingProfile(true); }}
            onSave={() => { setProfile({ ...profileDraft }); setEditingProfile(false); }}
            onCancel={() => setEditingProfile(false)}
          />
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
        <div style={{ display: "flex", gap: "20px", alignItems: "flex-start", flexWrap: "wrap" }}>

          {/* sidebar */}
          <div style={{ width: "240px", flexShrink: 0, display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={cardStyle}>
              <h3 style={{ ...h3Style, marginBottom: "14px" }}>Job Preferences</h3>
              <Field label="Desired Role" value={editingProfile ? profileDraft.desiredRole : profile.desiredRole} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, desiredRole: v })} />
              <Field label="Location" value={editingProfile ? profileDraft.location : profile.location} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, location: v })} />
              <Field label="Salary" value={editingProfile ? profileDraft.salary : profile.salary} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, salary: v })} />
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "4px" }}>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Open to opportunities</span>
                <div onClick={() => setProfile(p => ({ ...p, openToWork: !p.openToWork }))}
                  style={{ width: "36px", height: "20px", borderRadius: "10px", background: profile.openToWork ? "#2563eb" : "#334155", position: "relative", cursor: "pointer", transition: "background 0.2s" }}>
                  <div style={{ position: "absolute", top: "3px", left: profile.openToWork ? "19px" : "3px", width: "14px", height: "14px", borderRadius: "50%", background: "white", transition: "left 0.2s" }} />
                </div>
              </div>
            </div>
            <div style={cardStyle}>
              <h3 style={{ ...h3Style, marginBottom: "14px" }}>Activity</h3>
              {[["Job Results", 10], ["Applications", 8], ["Interviews", 2]].map(([l, v]) => (
                <div key={l} style={{ marginBottom: "12px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "5px" }}>
                    <span style={{ color: "#94a3b8", fontSize: "11px" }}>{l}</span>
                    <span style={{ color: "#60a5fa", fontWeight: 700, fontSize: "12px" }}>{v}</span>
                  </div>
                  <div style={{ height: "4px", background: "#0f172a", borderRadius: "4px" }}>
                    <div style={{ height: "100%", width: `${v * 10}%`, background: "linear-gradient(90deg,#2563eb,#60a5fa)", borderRadius: "4px" }} />
                  </div>
                </div>
              ))}
            </div>
            <div style={cardStyle}>
              <h3 style={{ ...h3Style, marginBottom: "14px" }}>Notifications</h3>
              {[
                { title: "New match: Senior Product Designer at TechCorp", time: "Just now", color: "#3b82f6" },
                { title: "Interview reminder: Innovate LLC tomorrow 10 AM", time: "1 day ago", color: "#f59e0b" },
                { title: "Your application at CreativeMinds was viewed", time: "3 days ago", color: "#10b981" },
              ].map((n, i) => (
                <div key={i} style={{ display: "flex", gap: "10px", alignItems: "flex-start", marginBottom: i < 2 ? "12px" : 0 }}>
                  <div style={{ width: "7px", height: "7px", borderRadius: "50%", background: n.color, flexShrink: 0, marginTop: "4px" }} />
                  <div>
                    <p style={{ fontSize: "11px", color: "#cbd5e1", lineHeight: 1.5, margin: "0 0 2px" }}>{n.title}</p>
                    <p style={{ fontSize: "10px", color: "#475569", margin: 0 }}>{n.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* main content */}
          <div style={{ flex: 1, minWidth: "280px" }}>

            {/* ── OVERVIEW ── */}
            {activeTab === "overview" && (
              <div style={cardStyle}>
                <div style={sectionHead}>
                  <h3 style={h3Style}>Profile Overview</h3>
                  <EditBar editing={editingProfile}
                    onEdit={() => { setProfileDraft({ ...profile }); setEditingProfile(true); }}
                    onSave={() => { setProfile({ ...profileDraft }); setEditingProfile(false); }}
                    onCancel={() => setEditingProfile(false)} />
                </div>
                <Field label="Full Name" value={editingProfile ? profileDraft.name : profile.name} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, name: v })} />
                <Field label="Email" value={editingProfile ? profileDraft.email : profile.email} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, email: v })} type="email" />
                <Field label="Bio" value={editingProfile ? profileDraft.bio : profile.bio} editing={editingProfile} onChange={v => setProfileDraft({ ...profileDraft, bio: v })} multiline />
              </div>
            )}

            {/* ── WORK & EDUCATION ── */}
            {activeTab === "work" && (
              <>
                {/* Work Experience */}
                <div style={cardStyle}>
                  <div style={sectionHead}>
                    <h3 style={h3Style}>Work Experience</h3>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      {editingWork && (
                        <button onClick={addWork} style={{ background: "#1e3a5f", color: "#60a5fa", border: "1px solid #2563eb", borderRadius: "8px", padding: "6px 12px", fontSize: "11px", cursor: "pointer" }}>+ Add</button>
                      )}
                      <EditBar editing={editingWork}
                        onEdit={() => { setWorkDraft(work.map(w => ({ ...w }))); setEditingWork(true); }}
                        onSave={() => { setWork([...workDraft]); setEditingWork(false); }}
                        onCancel={() => { setWorkDraft(work.map(w => ({ ...w }))); setEditingWork(false); }} />
                    </div>
                  </div>

                  {(editingWork ? workDraft : work).length === 0 && (
                    <p style={{ color: "#475569", fontSize: "13px", textAlign: "center", padding: "20px 0", margin: 0 }}>No entries. {editingWork ? 'Click "+ Add" to add one.' : ''}</p>
                  )}

                  {(editingWork ? workDraft : work).map((job, i, arr) => (
                    <div key={job.id} style={{ display: "flex", gap: "14px", paddingBottom: i < arr.length - 1 ? "18px" : 0, marginBottom: i < arr.length - 1 ? "18px" : 0, borderBottom: i < arr.length - 1 ? "1px solid #0f172a" : "none" }}>
                      <div style={{ width: "42px", height: "42px", borderRadius: "10px", background: job.color + "22", border: `1px solid ${job.color}44`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, color: job.color, fontWeight: 700, fontSize: "16px" }}>
                        {(job.company || "?")[0].toUpperCase()}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        {editingWork ? (
                          <>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
                              <div>
                                <p style={labelStyle}>Role</p>
                                <IN value={job.role} placeholder="Job title" onChange={e => updateWorkDraft(job.id, "role", e.target.value)} />
                              </div>
                              <div>
                                <p style={labelStyle}>Company</p>
                                <IN value={job.company} placeholder="Company name" onChange={e => updateWorkDraft(job.id, "company", e.target.value)} />
                              </div>
                            </div>
                            <div style={{ marginBottom: "8px" }}>
                              <p style={labelStyle}>Period</p>
                              <IN value={job.period} placeholder="e.g. Jan 2022 – Present" onChange={e => updateWorkDraft(job.id, "period", e.target.value)} />
                            </div>
                            <div style={{ marginBottom: "10px" }}>
                              <p style={labelStyle}>Description</p>
                              <TA rows={2} value={job.description} placeholder="Describe your role..." onChange={e => updateWorkDraft(job.id, "description", e.target.value)} />
                            </div>
                            <button className="rm-btn" onClick={() => removeWork(job.id)} style={{ background: "#450a0a", color: "#f87171", border: "1px solid #7f1d1d", borderRadius: "6px", padding: "4px 10px", fontSize: "11px", cursor: "pointer", transition: "all 0.2s" }}>
                              ✕ Remove
                            </button>
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

                {/* Education */}
                <div style={cardStyle}>
                  <div style={sectionHead}>
                    <h3 style={h3Style}>Education</h3>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      {editingEdu && (
                        <button onClick={addEdu} style={{ background: "#1e3a5f", color: "#60a5fa", border: "1px solid #2563eb", borderRadius: "8px", padding: "6px 12px", fontSize: "11px", cursor: "pointer" }}>+ Add</button>
                      )}
                      <EditBar editing={editingEdu}
                        onEdit={() => { setEduDraft(edu.map(e => ({ ...e }))); setEditingEdu(true); }}
                        onSave={() => { setEdu([...eduDraft]); setEditingEdu(false); }}
                        onCancel={() => { setEduDraft(edu.map(e => ({ ...e }))); setEditingEdu(false); }} />
                    </div>
                  </div>

                  {(editingEdu ? eduDraft : edu).length === 0 && (
                    <p style={{ color: "#475569", fontSize: "13px", textAlign: "center", padding: "20px 0", margin: 0 }}>No entries. {editingEdu ? 'Click "+ Add" to add one.' : ''}</p>
                  )}

                  {(editingEdu ? eduDraft : edu).map((e, i, arr) => (
                    <div key={e.id} style={{ display: "flex", gap: "14px", paddingBottom: i < arr.length - 1 ? "18px" : 0, marginBottom: i < arr.length - 1 ? "18px" : 0, borderBottom: i < arr.length - 1 ? "1px solid #0f172a" : "none" }}>
                      <div style={{ width: "42px", height: "42px", borderRadius: "10px", background: e.color + "22", border: `1px solid ${e.color}44`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, color: e.color, fontWeight: 700, fontSize: "16px" }}>
                        {(e.school || "?")[0].toUpperCase()}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        {editingEdu ? (
                          <>
                            <div style={{ marginBottom: "8px" }}>
                              <p style={labelStyle}>Degree</p>
                              <IN value={e.degree} placeholder="Degree / qualification" onChange={ev => updateEduDraft(e.id, "degree", ev.target.value)} />
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
                              <div>
                                <p style={labelStyle}>School</p>
                                <IN value={e.school} placeholder="Institution name" onChange={ev => updateEduDraft(e.id, "school", ev.target.value)} />
                              </div>
                              <div>
                                <p style={labelStyle}>GPA</p>
                                <IN value={e.gpa} placeholder="e.g. 3.8 / 4.0" onChange={ev => updateEduDraft(e.id, "gpa", ev.target.value)} />
                              </div>
                            </div>
                            <div style={{ marginBottom: "10px" }}>
                              <p style={labelStyle}>Period</p>
                              <IN value={e.period} placeholder="e.g. 2015 – 2019" onChange={ev => updateEduDraft(e.id, "period", ev.target.value)} />
                            </div>
                            <button className="rm-btn" onClick={() => removeEdu(e.id)} style={{ background: "#450a0a", color: "#f87171", border: "1px solid #7f1d1d", borderRadius: "6px", padding: "4px 10px", fontSize: "11px", cursor: "pointer", transition: "all 0.2s" }}>
                              ✕ Remove
                            </button>
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
                  <EditBar editing={editingContact}
                    onEdit={() => { setContactDraft({ ...contact }); setEditingContact(true); }}
                    onSave={() => { setContact({ ...contactDraft }); setEditingContact(false); }}
                    onCancel={() => setEditingContact(false)} />
                </div>
                <Field label="Email Address" value={editingContact ? contactDraft.email : contact.email} editing={editingContact} onChange={v => setContactDraft({ ...contactDraft, email: v })} type="email" />
                <Field label="Phone Number" value={editingContact ? contactDraft.phone : contact.phone} editing={editingContact} onChange={v => setContactDraft({ ...contactDraft, phone: v })} type="tel" />
                <Field label="Website / Portfolio" value={editingContact ? contactDraft.website : contact.website} editing={editingContact} onChange={v => setContactDraft({ ...contactDraft, website: v })} />
                <Field label="LinkedIn" value={editingContact ? contactDraft.linkedin : contact.linkedin} editing={editingContact} onChange={v => setContactDraft({ ...contactDraft, linkedin: v })} />
                <div style={{ marginTop: "16px", padding: "14px", background: "#0f172a", borderRadius: "12px", border: "1px solid #1e3a5f" }}>
                  <p style={{ ...labelStyle, marginBottom: "10px" }}>Quick Links</p>
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

            {/* ── LOCATION ── */}
            {activeTab === "location" && (
              <div style={cardStyle}>
                <div style={sectionHead}>
                  <h3 style={h3Style}>Where I Live</h3>
                  <EditBar editing={editingLocation}
                    onEdit={() => { setLocationDraft({ ...location }); setEditingLocation(true); }}
                    onSave={() => { setLocation({ ...locationDraft }); setEditingLocation(false); }}
                    onCancel={() => setEditingLocation(false)} />
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px", marginBottom: "4px" }}>
                  <Field label="City" value={editingLocation ? locationDraft.city : location.city} editing={editingLocation} onChange={v => setLocationDraft({ ...locationDraft, city: v })} />
                  <Field label="State / Province" value={editingLocation ? locationDraft.state : location.state} editing={editingLocation} onChange={v => setLocationDraft({ ...locationDraft, state: v })} />
                </div>
                <Field label="Country" value={editingLocation ? locationDraft.country : location.country} editing={editingLocation} onChange={v => setLocationDraft({ ...locationDraft, country: v })} />
                <div style={{ height: "150px", background: "#0f172a", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid #1e3a5f", flexDirection: "column", gap: "8px", margin: "4px 0 16px" }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="#3b82f6"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" /></svg>
                  <p style={{ color: "#475569", fontSize: "12px", margin: 0 }}>{location.city}, {location.state}, {location.country}</p>
                </div>
                <div style={{ background: "#0f172a", borderRadius: "10px", padding: "14px", border: "1px solid #1e3a5f" }}>
                  <p style={{ ...labelStyle, marginBottom: "10px" }}>Work Preference</p>
                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                    {["Remote", "Hybrid", "On-site"].map(opt => (
                      <span key={opt}
                        onClick={() => editingLocation && setLocationDraft({ ...locationDraft, workPref: opt })}
                        style={{
                          padding: "5px 14px", borderRadius: "20px", fontSize: "12px", fontWeight: 500,
                          cursor: editingLocation ? "pointer" : "default", transition: "all 0.2s",
                          background: (editingLocation ? locationDraft.workPref : location.workPref) === opt ? "#1e3a5f" : "#0f172a",
                          color: (editingLocation ? locationDraft.workPref : location.workPref) === opt ? "#60a5fa" : "#475569",
                          border: `1px solid ${(editingLocation ? locationDraft.workPref : location.workPref) === opt ? "#2563eb" : "#1e293b"}`,
                        }}>
                        {opt}
                      </span>
                    ))}
                  </div>
                  {editingLocation && <p style={{ color: "#475569", fontSize: "11px", marginTop: "8px", marginBottom: 0 }}>Click a chip to select your preference.</p>}
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
