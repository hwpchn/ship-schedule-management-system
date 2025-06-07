// 全局类型定义

// 用户相关类型
export interface User {
  id: number
  email: string
  username: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  date_joined: string
  last_login: string | null
  avatar?: string
}

// 认证相关类型
export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  first_name: string
  last_name: string
}

// 权限相关类型
export interface Permission {
  id: number
  name: string
  codename: string
  content_type: number
}

export interface Role {
  id: number
  name: string
  permissions: Permission[]
}

export interface UserPermissions {
  user_permissions: Permission[]
  group_permissions: Permission[]
  permissions: string[]
}

// 船舶相关类型
export interface VesselInfo {
  id: number
  vessel_name: string
  voyage: string
  departure_port: string
  arrival_port: string
  etd: string
  eta: string
  price: number
  gp_20: number
  hq_40: number
  cut_off_time: string
  created_at: string
  updated_at: string
}

export interface VesselEditData {
  price?: number
  gp_20?: number
  hq_40?: number
  cut_off_time?: string
}

// 本地费用相关类型
export interface LocalFee {
  id: number
  port: string
  fee_type: string
  amount: number
  currency: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LocalFeeFormData {
  port: string
  fee_type: string
  amount: number
  currency: string
  description: string
  is_active: boolean
}

// API 响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// 表单验证类型
export interface ValidationRule {
  required?: boolean
  message?: string
  trigger?: string | string[]
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}

export interface FormRules {
  [key: string]: ValidationRule[]
}

// 路由相关类型
export interface RouteMetaAuth {
  title: string
  requiresAuth?: boolean
  guest?: boolean
  permission?: string
}

// 组件 Props 类型
export interface DialogProps {
  visible: boolean
  title?: string
  width?: string
  destroyOnClose?: boolean
  closeOnClickModal?: boolean
}

// 状态管理类型
export interface AuthState {
  user: User | null
  token: string
  refreshToken: string
  loading: boolean
  permissions: string[]
  roles: Role[]
  authStatus: 'unknown' | 'initializing' | 'authenticated' | 'unauthenticated' | 'network_error'
  lastAuthCheck: number | null
  networkAvailable: boolean
  avatarVersion: number
}

export interface PermissionState {
  userPermissions: UserPermissions | null
  permissionsLoaded: boolean
  authStoreRef: any
}

// 工具类型
export type Nullable<T> = T | null
export type Optional<T> = T | undefined
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// 事件类型
export interface CustomEvent<T = any> {
  type: string
  data: T
  timestamp: number
}

// 日志类型
export interface LogEntry {
  level: 'error' | 'warn' | 'info' | 'debug'
  message: string
  data?: any
  timestamp: string
  module: string
}

// 环境变量类型
export interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly MODE: string
  readonly DEV: boolean
  readonly PROD: boolean
  readonly SSR: boolean
}

export interface ImportMeta {
  readonly env: ImportMetaEnv
}
