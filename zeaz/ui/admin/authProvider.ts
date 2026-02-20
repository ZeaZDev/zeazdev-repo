import { AuthProvider } from 'react-admin';

const authProvider: AuthProvider = {
  login: async ({ username, password }) => {
    localStorage.setItem('token', btoa(`${username}:${password}`));
  },
  logout: async () => {
    localStorage.removeItem('token');
  },
  checkAuth: async () => {
    if (!localStorage.getItem('token')) {
      throw new Error('Not authenticated');
    }
  },
  checkError: async () => undefined,
  getPermissions: async () => 'admin',
};

export default authProvider;
