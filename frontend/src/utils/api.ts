import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置 NProgress
NProgress.configure({
  showSpinner: false,
  minimum: 0.2,
  easing: 'ease',
  speed: 500,
})

class ApiClient {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: '/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        NProgress.start()
        return config
      },
      (error) => {
        NProgress.done()
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        NProgress.done()
        return response
      },
      (error) => {
        NProgress.done()
        
        const message = error.response?.data?.message || error.message || '请求失败'
        ElMessage.error(message)
        
        return Promise.reject(error)
      }
    )
  }

  // GET 请求
  async get<T = any>(url: string, params?: Record<string, any>): Promise<T> {
    const response = await this.instance.get(url, { params })
    return response.data
  }

  // POST 请求
  async post<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.instance.post(url, data)
    return response.data
  }

  // PUT 请求
  async put<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.instance.put(url, data)
    return response.data
  }

  // DELETE 请求
  async delete<T = any>(url: string): Promise<T> {
    const response = await this.instance.delete(url)
    return response.data
  }
}

export const apiClient = new ApiClient()
