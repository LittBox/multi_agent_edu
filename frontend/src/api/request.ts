import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
} from "axios";

/**
 * 后端统一响应结构。
 * 后端 router 层通过 api_success(...) 返回 { code, message, data }。
 */
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

/**
 * FastAPI 校验失败时 detail 可能是字符串，也可能是对象数组。
 */
type FastApiErrorDetail = string | Array<Record<string, unknown>> | Record<string, unknown>;

const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
});

/**
 * 请求拦截：自动携带登录 token。
 */
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

/**
 * 将 FastAPI 的 detail 转成人类可读的错误信息。
 */
function normalizeFastApiDetail(detail: FastApiErrorDetail | undefined): string | undefined {
  if (!detail) return undefined;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const loc = Array.isArray(item.loc) ? item.loc.join(".") : "";
        const msg = typeof item.msg === "string" ? item.msg : JSON.stringify(item);
        return loc ? `${loc}: ${msg}` : msg;
      })
      .join("; ");
  }
  return JSON.stringify(detail);
}

/**
 * 响应拦截：业务成功时直接返回 data。
 * 因此各 API 方法的 Promise<T> 中 T 就是后端 data 的类型。
 */
instance.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>): any => {
    const { code, message, data } = response.data;
    if (code !== 0) {
      return Promise.reject(new Error(message || "请求失败"));
    }
    return data;
  },
  (error) => {
    const detail = normalizeFastApiDetail(error.response?.data?.detail);
    const message = error.response?.data?.message ?? detail ?? error.message ?? "请求失败";
    return Promise.reject(new Error(message));
  }
);

type RequestClient = Omit<
  AxiosInstance,
  "get" | "post" | "put" | "patch" | "delete"
> & {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>;
  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>;
  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>;
  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>;
  patch<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>;
};

export default instance as RequestClient;
