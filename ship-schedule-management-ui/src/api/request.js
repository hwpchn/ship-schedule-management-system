import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 字段名映射
const getFieldName = field => {
  const fieldMap = {
    email: '邮箱',
    password: '密码',
    password_confirm: '确认密码',
    username: '用户名',
    phone: '手机号',
    name: '姓名',
  }
  return fieldMap[field] || field
}

// 是否正在刷新token的标记
let isRefreshing = false
// 待重试的请求队列
let failedQueue = []

// 处理队列中的请求
const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })

  failedQueue = []
}

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json;charset=UTF-8',
  },
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 添加认证token
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const { data } = response

    // 如果响应包含完整的自定义格式，直接返回
    if (data && typeof data.code !== 'undefined') {
      return data
    }

    // 否则包装为标准格式
    return {
      code: response.status,
      message: '请求成功',
      data,
    }
  },
  async error => {
    const { response, config } = error
    const authStore = useAuthStore()

    if (response) {
      const { status, data } = response
      let message = '请求失败' // 统一在这里声明message变量

      switch (status) {
        case 400:
          // 处理登录等业务逻辑错误
          message = '请求参数错误'

          // 如果是登录请求的错误
          if (config.url && config.url.includes('/auth/login/')) {
            if (data?.message) {
              // 处理常见的登录错误信息
              const loginErrorMap = {
                'Invalid credentials': '邮箱或密码错误，请重新输入',
                'Invalid email or password': '邮箱或密码错误，请重新输入',
                'Email not found': '该邮箱尚未注册',
                'Incorrect password': '密码错误，请重新输入',
                'User not found': '用户不存在',
                'Account disabled': '账户已被禁用，请联系管理员',
                'Account locked': '账户已被锁定，请稍后再试',
                'Too many failed attempts': '登录失败次数过多，请稍后再试',
              }

              message = loginErrorMap[data.message] || data.message || '登录失败，请检查邮箱和密码'
            } else {
              message = '登录失败，请检查邮箱和密码'
            }
          }
          // 如果是注册请求的错误
          else if (config.url && config.url.includes('/auth/register/')) {
            if (data?.message) {
              const registerErrorMap = {
                'Email already exists': '该邮箱已被注册，请使用其他邮箱',
                'Password too weak': '密码强度不足，请使用更复杂的密码',
                'Invalid email format': '邮箱格式不正确',
                'Passwords do not match': '两次输入的密码不一致',
              }

              message = registerErrorMap[data.message] || data.message || '注册失败'
            } else if (data && typeof data === 'object') {
              // 处理字段级错误
              const errors = []
              for (const [field, fieldErrors] of Object.entries(data)) {
                if (Array.isArray(fieldErrors)) {
                  fieldErrors.forEach(error => {
                    errors.push(`${getFieldName(field)}: ${error}`)
                  })
                }
              }
              if (errors.length > 0) {
                message = errors.join('; ')
              }
            } else {
              message = '注册失败，请检查输入信息'
            }
          }
          // 其他400错误
          else {
            if (data?.message) {
              message = data.message
            } else if (data && typeof data === 'object') {
              // 处理字段级错误
              const errors = []
              for (const [field, fieldErrors] of Object.entries(data)) {
                if (Array.isArray(fieldErrors)) {
                  fieldErrors.forEach(error => {
                    errors.push(`${getFieldName(field)}: ${error}`)
                  })
                }
              }
              if (errors.length > 0) {
                message = errors.join('; ')
              }
            }
          }

          // 在拦截器中不显示错误消息，让业务层处理
          // ElMessage.error(message)
          break

        case 401:
          // 如果是刷新token的请求失败，直接登出
          if (config.url && config.url.includes('/auth/token/refresh/')) {
            console.log('Refresh token 请求失败，清除认证信息')
            authStore.clearToken()
            isRefreshing = false
            processQueue(error, null)

            if (window.location.pathname !== '/login') {
              window.location.href = '/login'
            }
            ElMessage.error('登录已过期，请重新登录')
            return Promise.reject(error)
          }

          // token过期或无效，且用户已登录
          if (authStore.token) {
            // 如果正在刷新token，将请求加入队列
            if (isRefreshing) {
              try {
                await new Promise((resolve, reject) => {
                  failedQueue.push({ resolve, reject })
                })
                // 重新设置token并重试
                config.headers.Authorization = `Bearer ${authStore.token}`
                return request(config)
              } catch (err) {
                return Promise.reject(err)
              }
            }

            // 开始刷新token
            isRefreshing = true

            try {
              const refreshSuccess = await authStore.refreshAccessToken()
              if (refreshSuccess) {
                // 刷新成功，处理队列中的请求
                processQueue(null, authStore.token)
                // 重新发送原请求
                config.headers.Authorization = `Bearer ${authStore.token}`
                return request(config)
              } else {
                // 刷新失败
                processQueue(error, null)
                authStore.clearToken()
                if (window.location.pathname !== '/login') {
                  window.location.href = '/login'
                }
                ElMessage.error('登录已过期，请重新登录')
              }
            } catch (err) {
              // 刷新token出错
              processQueue(err, null)
              authStore.clearToken()
              if (window.location.pathname !== '/login') {
                window.location.href = '/login'
              }
              ElMessage.error('登录已过期，请重新登录')
            } finally {
              isRefreshing = false
            }
          } else {
            // 用户未登录
            if (window.location.pathname !== '/login') {
              window.location.href = '/login'
            }
            ElMessage.error('请先登录')
          }
          break

        case 403:
          ElMessage.error('没有权限访问此资源')
          break

        case 404:
          ElMessage.error('请求的资源不存在')
          break

        case 422:
          // 表单验证错误
          message = data?.message || '请求参数错误'

          // 如果有详细的字段错误信息，则显示
          if (data && typeof data === 'object') {
            const errors = []
            for (const [field, fieldErrors] of Object.entries(data)) {
              if (Array.isArray(fieldErrors)) {
                fieldErrors.forEach(error => {
                  errors.push(`${getFieldName(field)}: ${error}`)
                })
              }
            }
            if (errors.length > 0) {
              message = errors.join('; ')
            }
          }

          ElMessage.error(message)
          break

        case 500:
          ElMessage.error('服务器内部错误')
          break

        default:
          message = data?.message || `请求失败 (${status})`
          ElMessage.error(message)
      }

      // 返回标准错误格式
      return Promise.reject({
        code: status,
        message,
        data,
        response,
      })
    } else {
      // 网络错误
      ElMessage.error('网络连接失败，请检查网络')
      return Promise.reject({
        code: -1,
        message: '网络连接失败',
        data: null,
      })
    }
  }
)

export default request
