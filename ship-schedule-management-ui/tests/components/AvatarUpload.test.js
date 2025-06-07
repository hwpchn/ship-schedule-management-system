import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import AvatarUpload from '@/components/AvatarUpload.vue'
import { useAuthStore } from '@/stores/auth'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
  },
  ElMessageBox: {
    confirm: vi.fn(),
  },
}))

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  Upload: { name: 'Upload' },
  Delete: { name: 'Delete' },
  Camera: { name: 'Camera' },
  User: { name: 'User' },
}))

// Mock auth store
vi.mock('@/stores/auth')

// Mock avatar utils
vi.mock('@/utils/avatar', () => ({
  getUserAvatarUrl: vi.fn(() => 'https://example.com/avatar.jpg'),
}))

describe('AvatarUpload Component', () => {
  let wrapper
  let mockAuthStore

  beforeEach(() => {
    setActivePinia(createPinia())

    // Mock auth store
    mockAuthStore = {
      user: { id: 1, email: 'test@example.com' },
      avatarVersion: 1,
      uploadAvatar: vi.fn(),
      deleteAvatar: vi.fn(),
    }

    useAuthStore.mockReturnValue(mockAuthStore)

    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Component Rendering', () => {
    it('should render component successfully', () => {
      wrapper = mount(AvatarUpload)
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept size prop', () => {
      wrapper = mount(AvatarUpload, {
        props: { size: 150 },
      })
      expect(wrapper.props('size')).toBe(150)
    })

    it('should accept showActions prop', () => {
      wrapper = mount(AvatarUpload, {
        props: { showActions: false },
      })
      expect(wrapper.props('showActions')).toBe(false)
    })

    it('should accept showTips prop', () => {
      wrapper = mount(AvatarUpload, {
        props: { showTips: false },
      })
      expect(wrapper.props('showTips')).toBe(false)
    })
  })

  describe('File Upload Functionality', () => {
    beforeEach(() => {
      wrapper = mount(AvatarUpload)
    })

    it('should validate file type correctly', async () => {
      // Test invalid file type
      const invalidFile = new File([''], 'test.txt', { type: 'text/plain' })

      // Call the component's validation method directly
      const isValid = wrapper.vm.validateFile(invalidFile)

      expect(isValid).toBe(false)
      expect(ElMessage.error).toHaveBeenCalledWith('请选择 JPG、PNG 或 GIF 格式的图片')
    })

    it('should validate file size correctly', async () => {
      // Test oversized file (6MB)
      const oversizedFile = new File(['x'.repeat(6 * 1024 * 1024)], 'test.jpg', {
        type: 'image/jpeg',
      })

      const isValid = wrapper.vm.validateFile(oversizedFile)

      expect(isValid).toBe(false)
      expect(ElMessage.error).toHaveBeenCalledWith('图片大小不能超过 5MB')
    })

    it('should accept valid file', async () => {
      const validFile = new File([''], 'test.jpg', { type: 'image/jpeg' })

      const isValid = wrapper.vm.validateFile(validFile)

      expect(isValid).toBe(true)
    })

    it('should upload avatar successfully', async () => {
      ElMessageBox.confirm.mockResolvedValue('confirm')
      mockAuthStore.uploadAvatar.mockResolvedValue({ message: '上传成功' })

      const validFile = new File([''], 'test.jpg', { type: 'image/jpeg' })

      await wrapper.vm.uploadAvatar(validFile)

      expect(mockAuthStore.uploadAvatar).toHaveBeenCalledWith(validFile)
      expect(ElMessage.success).toHaveBeenCalledWith('上传成功')
      expect(wrapper.emitted('upload-success')).toBeTruthy()
    })

    it('should handle upload error', async () => {
      ElMessageBox.confirm.mockResolvedValue('confirm')
      const error = new Error('Upload failed')
      mockAuthStore.uploadAvatar.mockRejectedValue(error)

      const validFile = new File([''], 'test.jpg', { type: 'image/jpeg' })

      await wrapper.vm.uploadAvatar(validFile)

      expect(ElMessage.error).toHaveBeenCalledWith('Upload failed')
      expect(wrapper.emitted('upload-error')).toBeTruthy()
    })
  })

  describe('Avatar Deletion', () => {
    beforeEach(() => {
      wrapper = mount(AvatarUpload)
    })

    it('should delete avatar successfully', async () => {
      ElMessageBox.confirm.mockResolvedValue('confirm')
      mockAuthStore.deleteAvatar.mockResolvedValue({ message: '删除成功' })

      await wrapper.vm.handleDeleteAvatar()

      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        '确定要删除当前头像吗？删除后将显示默认头像。',
        '确认删除',
        expect.any(Object)
      )
      expect(mockAuthStore.deleteAvatar).toHaveBeenCalled()
      expect(ElMessage.success).toHaveBeenCalledWith('删除成功')
      expect(wrapper.emitted('delete-success')).toBeTruthy()
    })

    it('should handle delete cancellation', async () => {
      ElMessageBox.confirm.mockRejectedValue('cancel')

      await wrapper.vm.handleDeleteAvatar()

      expect(mockAuthStore.deleteAvatar).not.toHaveBeenCalled()
    })
  })

  describe('Event Emissions', () => {
    beforeEach(() => {
      wrapper = mount(AvatarUpload)
    })

    it('should emit upload-success event', async () => {
      ElMessageBox.confirm.mockResolvedValue('confirm')
      mockAuthStore.uploadAvatar.mockResolvedValue({ message: '上传成功' })

      const validFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      await wrapper.vm.uploadAvatar(validFile)

      expect(wrapper.emitted('upload-success')).toBeTruthy()
    })

    it('should emit upload-error event', async () => {
      ElMessageBox.confirm.mockResolvedValue('confirm')
      const error = new Error('Upload failed')
      mockAuthStore.uploadAvatar.mockRejectedValue(error)

      const validFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      await wrapper.vm.uploadAvatar(validFile)

      expect(wrapper.emitted('upload-error')).toBeTruthy()
    })
  })
})
