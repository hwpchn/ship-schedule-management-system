import { describe, it, expect, beforeEach, vi } from 'vitest'
import { logger, createLogger, permissionLogger } from '@/utils/logger'

// Mock import.meta.env
Object.defineProperty(import.meta, 'env', {
  value: {
    MODE: 'development', // 设置为development以便测试permission方法
  },
  writable: true,
})

describe('Logger', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset console mocks
    console.log = vi.fn()
    console.info = vi.fn()
    console.warn = vi.fn()
    console.error = vi.fn()
  })

  describe('default logger', () => {
    it('should log error messages', () => {
      logger.error('Test error message')
      expect(console.error).toHaveBeenCalled()
    })

    it('should log warning messages', () => {
      logger.warn('Test warning message')
      expect(console.warn).toHaveBeenCalled()
    })

    it('should log info messages', () => {
      logger.info('Test info message')
      expect(console.info).toHaveBeenCalled()
    })

    it('should log debug messages', () => {
      logger.debug('Test debug message')
      expect(console.log).toHaveBeenCalled()
    })

    it('should format messages correctly', () => {
      logger.info('Test message', { key: 'value' })
      expect(console.info).toHaveBeenCalledWith(
        expect.stringContaining('[INFO] [App]'),
        'Test message',
        { key: 'value' }
      )
    })
  })

  describe('createLogger', () => {
    it('should create logger with custom module name', () => {
      const customLogger = createLogger('TestModule')
      customLogger.info('Test message')

      expect(console.info).toHaveBeenCalledWith(
        expect.stringContaining('[INFO] [TestModule]'),
        'Test message',
        ''
      )
    })
  })

  describe('permissionLogger', () => {
    it('should have correct module name', () => {
      permissionLogger.info('Permission test')

      expect(console.info).toHaveBeenCalledWith(
        expect.stringContaining('[INFO] [Permission]'),
        'Permission test',
        ''
      )
    })

    it('should log permission-specific messages', () => {
      // 直接测试debug方法，因为permission方法内部调用debug
      permissionLogger.debug('Permission check', { permission: 'user.list' })

      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[DEBUG] [Permission]'),
        'Permission check',
        { permission: 'user.list' }
      )
    })
  })

  describe('formatMessage', () => {
    it('should include timestamp and module info', () => {
      const testLogger = createLogger('Test')
      const formatted = testLogger.formatMessage('INFO', 'Test message')

      expect(formatted.prefix).toMatch(
        /\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\] \[INFO\] \[Test\]/
      )
      expect(formatted.message).toBe('Test message')
    })

    it('should handle data parameter', () => {
      const testLogger = createLogger('Test')
      const testData = { key: 'value' }
      const formatted = testLogger.formatMessage('INFO', 'Test message', testData)

      expect(formatted.data).toBe(testData)
    })
  })
})
