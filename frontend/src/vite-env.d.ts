/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the backend API, e.g. https://api.example.com/api/v1 */
  readonly VITE_API_BASE_URL?: string
  /** Health endpoint of the backend, e.g. https://api.example.com/health */
  readonly VITE_HEALTH_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
