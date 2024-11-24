import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
});

// add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response.status === 401) {
      localStorage.removeItem("token");
      if (typeof window !== "undefined") {
        // let the component handle the rediret
        window.dispatchEvent(new Event("auth:failed"));
      }
    }
    return Promise.reject(error);
  },
);

export default api;
