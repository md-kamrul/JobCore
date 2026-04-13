import { supabase } from './supabaseClient';

// ─── PROFILE ───

export async function getProfile(userId) {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single();
  return { data, error };
}

export async function updateProfile(userId, updates) {
  const { data, error } = await supabase
    .from('profiles')
    .update(updates)
    .eq('id', userId)
    .select()
    .single();
  return { data, error };
}

// ─── AVATAR ───

export async function uploadAvatar(userId, file) {
  const ext = file.name.split('.').pop();
  const path = `${userId}/avatar.${ext}`;

  const { error: uploadError } = await supabase.storage
    .from('avatars')
    .upload(path, file, { upsert: true });

  if (uploadError) return { url: null, error: uploadError };

  const { data } = supabase.storage.from('avatars').getPublicUrl(path);
  return { url: data.publicUrl, error: null };
}

// ─── CV ───

export async function uploadCV(userId, file) {
  const ext = file.name.split('.').pop();
  const path = `${userId}/cv.${ext}`;

  const { error: uploadError } = await supabase.storage
    .from('cvs')
    .upload(path, file, { upsert: true });

  if (uploadError) return { path: null, error: uploadError };
  return { path, error: null };
}

export async function getCVSignedUrl(userId, fileName) {
  const ext = fileName.split('.').pop();
  const path = `${userId}/cv.${ext}`;

  const { data, error } = await supabase.storage
    .from('cvs')
    .createSignedUrl(path, 60 * 60); // 1 hour expiry

  return { url: data?.signedUrl ?? null, error };
}

export async function deleteCV(userId, fileName) {
  const ext = fileName.split('.').pop();
  const path = `${userId}/cv.${ext}`;
  return await supabase.storage.from('cvs').remove([path]);
}

// ─── WORK EXPERIENCE ───

export async function getWorkExperience(profileId) {
  const { data, error } = await supabase
    .from('work_experience')
    .select('*')
    .eq('profile_id', profileId)
    .order('sort_order');
  return { data, error };
}

export async function saveWorkExperience(profileId, entries) {
  // Delete all existing, then re-insert (simplest approach)
  await supabase.from('work_experience').delete().eq('profile_id', profileId);

  if (entries.length === 0) return { error: null };

  const rows = entries.map((e, i) => ({
    profile_id: profileId,
    role: e.role,
    company: e.company,
    period: e.period,
    description: e.description,
    color: e.color,
    sort_order: i,
  }));

  const { error } = await supabase.from('work_experience').insert(rows);
  return { error };
}

// ─── EDUCATION ───

export async function getEducation(profileId) {
  const { data, error } = await supabase
    .from('education')
    .select('*')
    .eq('profile_id', profileId)
    .order('sort_order');
  return { data, error };
}

export async function saveEducation(profileId, entries) {
  await supabase.from('education').delete().eq('profile_id', profileId);

  if (entries.length === 0) return { error: null };

  const rows = entries.map((e, i) => ({
    profile_id: profileId,
    degree: e.degree,
    school: e.school,
    period: e.period,
    gpa: e.gpa,
    color: e.color,
    sort_order: i,
  }));

  const { error } = await supabase.from('education').insert(rows);
  return { error };
}