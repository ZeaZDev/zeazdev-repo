import { DataProvider, fetchUtils } from 'react-admin';

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const httpClient = async (url: string, options: fetchUtils.Options = {}) => {
  const token = localStorage.getItem('token');
  const headers = new Headers(options.headers || { Accept: 'application/json' });
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return fetchUtils.fetchJson(url, { ...options, headers });
};

const oneItemList = async (path: string) => {
  const { json } = await httpClient(`${apiUrl}${path}`);
  const data = Array.isArray(json) ? json : [json];
  return { data, total: data.length };
};

const dataProvider: DataProvider = {
  getList: async (resource) => {
    if (resource === 'tiktok_jobs') {
      const { json } = await httpClient(`${apiUrl}/tiktok/jobs`);
      const data = (json.data || []).map((item: any) => ({ ...item, id: item.id }));
      return { data, total: data.length };
    }
    if (resource === 'admin_panel') {
      return oneItemList('/admin/control-panel');
    }
    if (resource === 'user_panel') {
      return oneItemList('/user/control-panel');
    }
    return { data: [], total: 0 };
  },

  getOne: async (resource, params) => {
    if (resource === 'tiktok_jobs') {
      const { json } = await httpClient(`${apiUrl}/tiktok/jobs/${params.id}`);
      return { data: { ...json, id: json.id } };
    }
    throw new Error(`Unsupported resource getOne: ${resource}`);
  },

  create: async (resource, params) => {
    if (resource === 'tiktok_feed_forms') {
      const { json } = await httpClient(`${apiUrl}/tiktok/feed-product-form/generate`, {
        method: 'POST',
        body: JSON.stringify(params.data),
      });
      return { data: { ...json, id: json.id } };
    }
    if (resource === 'tiktok_videos') {
      const { json } = await httpClient(`${apiUrl}/tiktok/video/generate`, {
        method: 'POST',
        body: JSON.stringify(params.data),
      });
      return { data: { ...json, id: json.id } };
    }
    if (resource === 'tiktok_uploads') {
      const { json } = await httpClient(`${apiUrl}/tiktok/shop-affiliate/upload`, {
        method: 'POST',
        body: JSON.stringify(params.data),
      });
      return { data: { ...json, id: json.id } };
    }
    throw new Error(`Unsupported resource create: ${resource}`);
  },

  getMany: async () => ({ data: [] }),
  getManyReference: async () => ({ data: [], total: 0 }),
  update: async () => {
    throw new Error('Not implemented');
  },
  updateMany: async () => ({ data: [] }),
  delete: async () => {
    throw new Error('Not implemented');
  },
  deleteMany: async () => ({ data: [] }),
};

export default dataProvider;
