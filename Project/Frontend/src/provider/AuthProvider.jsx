import { createContext, useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

export const AuthContext = createContext(null);

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const createUser = (email, password, fullName) => {
    return supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: fullName }
      }
    });
  };

  const loginUser = (email, password) => {
    return supabase.auth.signInWithPassword({ email, password });
  };

  const loginWithGoogle = () => {
    return supabase.auth.signInWithOAuth({ provider: 'google' });
  };

  const logoutUser = () => {
    return supabase.auth.signOut();
  };

  return (
    <AuthContext.Provider value={{ user, loading, createUser, loginUser, loginWithGoogle, logoutUser }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}