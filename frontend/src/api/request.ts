import axios, {
  type AxiosInstance,
  type AxiosResponse,
} from "axios";

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
});

instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

instance.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { code, message, data } = response.data;

    if (code !== 0) {
      return Promise.reject(new Error(message));
    }

    return data;
  },
  (error) => Promise.reject(error)
);

export default instance;