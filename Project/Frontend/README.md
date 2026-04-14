# Frontend

React + Vite frontend for JobCore.

## Features

- Authentication with Supabase Auth (email/password + Google OAuth)
- Protected routes for main AI features
- Job Agent chat interface and Google Form apply flow UI
- ATS Resume Checker page with upload and result tabs
- Profile page with:
	- Avatar upload
	- CV upload/download
	- Work and education management
	- Contact info and personal summary
- Dashboard and Home pages for feature navigation

## Tech Stack

- React 19
- Vite
- React Router
- Tailwind CSS 4
- Supabase JS
- Firebase SDK (present for config compatibility)
- React Icons

## Install

```bash
npm install
```

## Run

```bash
npm run dev
```

Default local URL: http://localhost:5173

## Build

```bash
npm run build
npm run preview
```

## Environment Variables

Create .env.local in this folder:

```env
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

# Optional Firebase keys
VITE_apiKey=
VITE_authDomain=
VITE_projectId=
VITE_storageBucket=
VITE_messagingSenderId=
VITE_appId=
```

## Backend Dependencies

This frontend expects these backend services to be running:

- Job Agent API: http://localhost:5001
- Resume Checker API: http://localhost:5004
- Mock Interview API: http://localhost:5002 (available backend, not fully wired in current page)

## Route Map

- / -> Home
- /dashboard -> Feature dashboard
- /login -> Login
- /signup -> Signup
- /profile -> Profile and CV management
- /job-agent -> Protected Job Agent page
- /resume-checker -> Protected Resume Checker page
- /mock-interview -> Protected mock interview page

## Key Integration Points

- Auth context: src/provider/AuthProvider.jsx
- Supabase client: src/lib/supabaseClient.js
- Profile service: src/lib/profileService.js
- Job Agent page API calls: src/pages/JobAgent.jsx
- Resume checker page API calls: src/pages/ResumeChecker.jsx

## Supabase Data Expectations

The frontend expects these resources:

- Table: profiles
- Table: work_experience
- Table: education
- Storage bucket: avatars
- Storage bucket: cvs

Expected profile-related fields include:

- id, full_name, email, bio, desired_role, phone, website, linkedin, avatar_url
- cv_name, cv_size, cv_type, cv_uploaded_at, cv_note

## Notes

- Mock Interview page currently links to an external voice interview demo and shows text mode as coming soon.
- Some pages are placeholders for future modules (for example, cover letter generator and tracker links in dashboard).

## Troubleshooting

- White screen on startup:
	- Confirm .env.local values are present.
	- Confirm npm install completed successfully.
- Login/signup not working:
	- Check Supabase URL/key and auth providers.
- Job agent not responding:
	- Ensure backend on port 5001 is running.
- Resume checker connection error:
	- Ensure backend on port 5004 is running.