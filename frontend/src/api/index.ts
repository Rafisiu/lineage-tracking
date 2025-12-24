import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 300000, // 5 minutes for long queries
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Only redirect to login if not an /auth/login request
    const originalRequest = error.config;
    if (
      error.response?.status === 401 &&
      !(originalRequest && originalRequest.url && originalRequest.url.includes("/auth/login"))
    ) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    api.post("/auth/login", { username, password }),

  logout: (refreshToken: string) =>
    api.post("/auth/logout", { refresh_token: refreshToken }),

  refreshToken: (refreshToken: string) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),

  getCurrentUser: () => api.get("/auth/me"),
};

// Query API
export const queryApi = {
  execute: (query: string, format: string = "JSON") =>
    api.post("/query/execute", { query, format }),

  health: () => api.get("/query/health"),
};

// Migration API
export const migrationApi = {
  analyzeSource: (data: any) => api.post("/migration/analyze-source", data),

  suggestMapping: (data: any) => api.post("/migration/suggest-mapping", data),

  execute: (data: any) => api.post("/migration/execute", data),

  getStatus: (migrationId: string) =>
    api.get(`/migration/status/${migrationId}`),

  getHistory: (params?: { limit?: number; offset?: number; status?: string }) =>
    api.get("/migration/history", { params }),

  getTables: (schema: string = "public") =>
    api.get("/migration/tables", { params: { schema } }),
};

// S3 Explorer API
export const s3Api = {
  // Buckets
  listBuckets: () => api.get("/s3/buckets"),

  createBucket: (bucketName: string) => api.post(`/s3/buckets/${bucketName}`),

  // Files
  browse: (bucket: string, prefix: string = "", recursive: boolean = false) =>
    api.get(`/s3/browse/${bucket}`, { params: { prefix, recursive } }),

  getFileInfo: (bucket: string, path: string) =>
    api.get(`/s3/info/${bucket}/${path}`),

  deleteFile: (bucket: string, path: string) =>
    api.delete(`/s3/file/${bucket}/${path}`),

  getDownloadUrl: (bucket: string, path: string) =>
    api.get(`/s3/download-url/${bucket}/${path}`),

  // Query
  query: (bucket: string, path: string, query?: string, limit: number = 1000) =>
    api.post("/s3/query", { bucket, path, query, limit }),

  rawSql: (query: string) => api.post("/s3/query/sql", { query }),

  getSchema: (bucket: string, path: string) =>
    api.get(`/s3/schema/${bucket}/${path}`),

  preview: (bucket: string, path: string, limit: number = 100) =>
    api.get(`/s3/preview/${bucket}/${path}`, { params: { limit } }),

  health: () => api.get("/s3/health"),
};

export default api;
