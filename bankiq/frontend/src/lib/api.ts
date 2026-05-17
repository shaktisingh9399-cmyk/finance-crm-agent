/** Axios HTTP client with JWT interceptors — tokens held in memory via authStore. */

import axios from "axios";

import { useAuthStore } from "@/store/authStore";
import { AuthScheme, HttpContentType, HttpHeader, HttpStatus } from "@/types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { [HttpHeader.ContentType]: HttpContentType.Json },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers[HttpHeader.Authorization] = `${AuthScheme.Bearer} ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === HttpStatus.Unauthorized && !original._retry) {
      original._retry = true;
      const refreshed = await useAuthStore.getState().refreshAccessToken();
      if (refreshed) {
        original.headers[HttpHeader.Authorization] =
          `${AuthScheme.Bearer} ${useAuthStore.getState().accessToken}`;
        return api(original);
      }
    }
    return Promise.reject(error);
  },
);
