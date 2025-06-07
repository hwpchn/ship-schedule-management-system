/**
 * 统一的日志工具
 * 在开发环境输出日志，生产环境可配置是否输出
 */

const isDevelopment = import.meta.env.MODE === 'development'
const isProduction = import.meta.env.MODE === 'production'

// 日志级别
const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3,
}

// 当前日志级别（生产环境只输出错误和警告）
const currentLevel = isProduction ? LOG_LEVELS.WARN : LOG_LEVELS.DEBUG

class Logger {
  constructor(module = 'App') {
    this.module = module
  }

  /**
   * 格式化日志消息
   */
  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString()
    const prefix = `[${timestamp}] [${level}] [${this.module}]`

    if (data) {
      return { prefix, message, data }
    }
    return { prefix, message }
  }

  /**
   * 错误日志
   */
  error(message, data = null) {
    if (currentLevel >= LOG_LEVELS.ERROR) {
      const formatted = this.formatMessage('ERROR', message, data)
      console.error(formatted.prefix, formatted.message, formatted.data || '')
    }
  }

  /**
   * 警告日志
   */
  warn(message, data = null) {
    if (currentLevel >= LOG_LEVELS.WARN) {
      const formatted = this.formatMessage('WARN', message, data)
      console.warn(formatted.prefix, formatted.message, formatted.data || '')
    }
  }

  /**
   * 信息日志
   */
  info(message, data = null) {
    if (currentLevel >= LOG_LEVELS.INFO) {
      const formatted = this.formatMessage('INFO', message, data)
      console.info(formatted.prefix, formatted.message, formatted.data || '')
    }
  }

  /**
   * 调试日志
   */
  debug(message, data = null) {
    if (currentLevel >= LOG_LEVELS.DEBUG) {
      const formatted = this.formatMessage('DEBUG', message, data)
      console.log(formatted.prefix, formatted.message, formatted.data || '')
    }
  }

  /**
   * 权限相关日志
   */
  permission(message, data = null) {
    if (isDevelopment) {
      const formatted = this.formatMessage('PERMISSION', message, data)
      console.log('🔐', formatted.prefix, formatted.message, formatted.data || '')
    }
  }

  /**
   * 路由相关日志
   */
  router(message, data = null) {
    if (isDevelopment) {
      const formatted = this.formatMessage('ROUTER', message, data)
      console.log('🛣️', formatted.prefix, formatted.message, formatted.data || '')
    }
  }

  /**
   * API相关日志
   */
  api(message, data = null) {
    if (isDevelopment) {
      const formatted = this.formatMessage('API', message, data)
      console.log('📡', formatted.prefix, formatted.message, formatted.data || '')
    }
  }
}

// 创建默认logger实例
export const logger = new Logger()

// 创建模块特定的logger
export const createLogger = module => new Logger(module)

// 权限模块logger
export const permissionLogger = new Logger('Permission')

// 路由模块logger
export const routerLogger = new Logger('Router')

// API模块logger
export const apiLogger = new Logger('API')

export default logger
