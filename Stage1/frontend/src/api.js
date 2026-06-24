import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001/api/v1',
});

// Interceptor to attach the JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Interceptor to handle 401 Unauthorized errors and refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/token/refresh/') {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        try {
          // Use axios directly so we don't get caught in the interceptor loop
          const res = await axios.post('http://localhost:8001/api/v1/auth/token/refresh/', { 
            refresh: refreshToken 
          });
          
          localStorage.setItem('access_token', res.data.access);
          
          // Update the failed request with the new token
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
          
          // Retry the original request
          return axios(originalRequest);
        } catch (refreshError) {
          // If the refresh token is also invalid/expired, log out
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          // Optional: redirect to login or let the app handle the missing token
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
