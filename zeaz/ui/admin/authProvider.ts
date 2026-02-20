import { AuthProvider } from 'react-admin';

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const authProvider: AuthProvider = {
  login: async ({ username }) => {
    const role = username === 'admin' ? 'admin' : username === 'finance' ? 'finance' : 'user';
    const response = await fetch(`${apiUrl}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: username, role }),
    });

    if (!response.ok) {
      throw new Error('Authentication failed');
    }

    const json = await response.json();
    localStorage.setItem('token', json.access_token);
    localStorage.setItem('role', role);
  },

  logout: async () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
  },

  checkAuth: async () => {
    if (!localStorage.getItem('token')) {
      throw new Error('Not authenticated');
    }
  },

  checkError: async () => undefined,
  getPermissions: async () => localStorage.getItem('role') ?? 'user',
};

export default authProvider;
