import axios, { AxiosInstance, AxiosResponse } from "axios";
import { ElMessage } from "element-plus";
import NProgress from "nprogress";
import "nprogress/nprogress.css";

// 配置 NProgress
NProgress.configure({
  showSpinner: false,
  minimum: 0.2,
  easing: "ease",
  speed: 500,
});

class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: "/api/v1",
      timeout: 10000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        NProgress.start();
        
        // Inject token
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        return config;
      },
      (error) => {
        NProgress.done();
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        NProgress.done();
        return response;
      },
      (error) => {
        NProgress.done();

        // Handle 401 Unauthorized
        if (error.response?.status === 401) {
            // Check if we are already on login page to avoid loops or unnecessary messages
            if (!window.location.pathname.includes('/login')) {
                ElMessage.error('Session expired. Please login again.');
                localStorage.removeItem('access_token');
                // Redirect to login using window.location since we can't easily access router here
                // properly without circular dependency or extra setup.
                // Or use a callback. For now, simple redirect.
                // window.location.href = '/login'; // Let's avoid hard reload if possible, but safe.
                // Actually, let's just clear token. The router guard should handle redirect if page requires auth.
                // But for user experience, better to redirect or let the store handle it.
                // Since api.ts is low level, clearing storage is safe.
            }
        } else {
            const message =
            error.response?.data?.detail || 
            error.response?.data?.message || 
            error.message || 
            "请求失败";
            
            // Prefer 'detail' from FastAPI
            
            ElMessage.error(message);
        }

        return Promise.reject(error);
      }
    );
  }

  // GET 请求
  async get<T = any>(url: string, params?: Record<string, any>): Promise<T> {
    // Ensure trailing slash for FastAPI compatibility
    // This prevents 307 redirects that cause CORS errors
    const normalizedUrl = url.endsWith("/") ? url : `${url}/`;
    const response = await this.instance.get(normalizedUrl, { params });
    return response.data;
  }

  // POST 请求
  async post<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.instance.post(url, data);
    return response.data;
  }

  // PUT 请求
  async put<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.instance.put(url, data);
    return response.data;
  }

  // DELETE 请求
  async delete<T = any>(url: string): Promise<T> {
    const response = await this.instance.delete(url);
    return response.data;
  }
}

export const apiClient = new ApiClient();
