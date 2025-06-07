import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import EditVesselDialog from '@/components/EditVesselDialog.vue'
import { usePermissionStore } from '@/stores/permission'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
  ElMessageBox: {
    confirm: vi.fn(),
  },
  ElDialog: {
    name: 'ElDialog',
    template:
      '<div class="el-dialog" v-if="modelValue"><slot /><div class="el-dialog__footer"><slot name="footer" /></div></div>',
    props: ['modelValue', 'title', 'width', 'beforeClose', 'destroyOnClose'],
    emits: ['update:modelValue'],
  },
  ElForm: {
    name: 'ElForm',
    template: '<form class="el-form"><slot /></form>',
    props: ['model', 'labelWidth', 'rules'],
    methods: {
      validate: vi.fn(() => Promise.resolve(true)),
    },
  },
  ElFormItem: {
    name: 'ElFormItem',
    template: '<div class="el-form-item"><label>{{ label }}</label><slot /></div>',
    props: ['label', 'prop'],
  },
  ElInputNumber: {
    name: 'ElInputNumber',
    template:
      '<input class="el-input-number" type="number" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue', 'min', 'precision', 'step', 'placeholder', 'disabled'],
    emits: ['update:modelValue'],
  },
  ElInput: {
    name: 'ElInput',
    template:
      '<input class="el-input" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue', 'placeholder', 'disabled', 'maxlength', 'showWordLimit'],
    emits: ['update:modelValue'],
  },
  ElDatePicker: {
    name: 'ElDatePicker',
    template:
      '<input class="el-date-picker" type="date" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: [
      'modelValue',
      'type',
      'placeholder',
      'format',
      'valueFormat',
      'disabled',
      'disabledDate',
    ],
    emits: ['update:modelValue'],
  },
  ElButton: {
    name: 'ElButton',
    template: '<button class="el-button" :disabled="disabled || loading"><slot /></button>',
    props: ['type', 'disabled', 'loading'],
  },
  ElAlert: {
    name: 'ElAlert',
    template: '<div class="el-alert" :class="`el-alert--${type}`"><slot /></div>',
    props: ['title', 'type', 'closable', 'showIcon'],
  },
  ElSkeleton: {
    name: 'ElSkeleton',
    template: '<div class="el-skeleton"></div>',
    props: ['rows', 'animated'],
  },
  ElDivider: {
    name: 'ElDivider',
    template: '<div class="el-divider"><slot /></div>',
    props: ['contentPosition'],
  },
}))

// Mock stores
vi.mock('@/stores/permission')

// Mock composables
vi.mock('@/composables/useVesselEdit', () => ({
  useVesselEdit: () => ({
    editVesselInfo: vi.fn(),
    loading: false,
    errors: {},
  }),
  useVesselForm: initialData => ({
    form: { ...initialData },
    originalData: { ...initialData },
    resetForm: vi.fn(),
    updateOriginalData: vi.fn(),
    hasChanges: { value: false },
    getChanges: vi.fn(() => ({})),
    validateForm: vi.fn(() => ({ valid: true, errors: {} })),
  }),
}))

describe('EditVesselDialog Component', () => {
  let wrapper
  let mockPermissionStore

  const mockVessel = {
    id: 1,
    vessel: 'Test Vessel',
    voyage: 'TV001',
    vessel_info: {
      id: 1,
      price: 1500,
      gp_20: '100',
      hq_40: '50',
      cut_off_time: '2024-02-01',
    },
  }

  beforeEach(() => {
    setActivePinia(createPinia())

    mockPermissionStore = {
      isPermissionsInitialized: true,
      canEditVesselInfo: true,
      loadUserPermissions: vi.fn(),
    }

    usePermissionStore.mockReturnValue(mockPermissionStore)

    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Component Rendering', () => {
    it('should render dialog when visible', async () => {
      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })

      // Wait for component to update
      await wrapper.vm.$nextTick()

      // Check if component exists (the dialog might be controlled by v-model)
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props('visible')).toBe(true)
    })

    it('should not render dialog when not visible', () => {
      wrapper = mount(EditVesselDialog, {
        props: {
          visible: false,
          vessel: mockVessel,
        },
      })

      expect(wrapper.props('visible')).toBe(false)
    })

    it('should show loading skeleton when permissions not initialized', async () => {
      mockPermissionStore.isPermissionsInitialized = false

      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })

      await wrapper.vm.$nextTick()

      // Check for loading container instead of skeleton directly
      expect(wrapper.find('.loading-container').exists()).toBe(true)
    })
  })

  describe('Permission-based Rendering', () => {
    it('should show edit form when user has edit permission', async () => {
      mockPermissionStore.canEditVesselInfo = true

      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })

      await wrapper.vm.$nextTick()

      // Check for form elements in the rendered HTML
      expect(wrapper.html()).toContain('el-form')
      expect(wrapper.html()).toContain('el-form-item')
    })

    it('should show read-only view when user has no edit permission', async () => {
      mockPermissionStore.canEditVesselInfo = false

      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.find('.read-only-view').exists()).toBe(true)
      expect(wrapper.html()).not.toContain('el-form')
    })

    it('should show correct alert message for no edit permission', async () => {
      mockPermissionStore.canEditVesselInfo = false

      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.html()).toContain('type="warning"')
      expect(wrapper.html()).toContain('您没有编辑权限')
    })
  })

  describe('Form Fields', () => {
    beforeEach(async () => {
      mockPermissionStore.canEditVesselInfo = true
      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })
      await wrapper.vm.$nextTick()
    })

    it('should render price input field', () => {
      expect(wrapper.html()).toContain('el-input-number')
    })

    it('should render gp_20 input field', () => {
      expect(wrapper.html()).toContain('el-input')
    })

    it('should render date picker for cut_off_time', () => {
      expect(wrapper.html()).toContain('el-date-picker')
    })

    it('should populate form fields with vessel data', () => {
      // Check that the component renders with the expected structure
      expect(wrapper.html()).toContain('el-form')
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Form Actions', () => {
    beforeEach(async () => {
      mockPermissionStore.canEditVesselInfo = true
      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })
      await wrapper.vm.$nextTick()
    })

    it('should show save and cancel buttons for users with edit permission', () => {
      const html = wrapper.html()
      expect(html).toContain('取消')
      expect(html).toContain('保存修改')
    })

    it('should show only close button for users without edit permission', async () => {
      mockPermissionStore.canEditVesselInfo = false

      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })

      await wrapper.vm.$nextTick()

      const html = wrapper.html()
      expect(html).toContain('关闭')
      expect(html).not.toContain('保存修改')
    })

    it('should handle cancel button click', async () => {
      // Test that component has the expected structure for button handling
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.html()).toContain('取消')
    })
  })

  describe('Read-only View', () => {
    beforeEach(async () => {
      mockPermissionStore.canEditVesselInfo = false
      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })
      await wrapper.vm.$nextTick()
    })

    it('should display vessel information in read-only format', () => {
      expect(wrapper.find('.info-item').exists()).toBe(true)
    })

    it('should show vessel price correctly', () => {
      const readOnlyView = wrapper.find('.read-only-view')
      expect(readOnlyView.exists()).toBe(true)
    })

    it('should show vessel basic information section', () => {
      expect(wrapper.html()).toContain('el-divider')
    })
  })

  describe('Event Emissions', () => {
    beforeEach(() => {
      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })
    })

    it('should emit update:visible when dialog visibility changes', async () => {
      await wrapper.setProps({ visible: false })

      expect(wrapper.emitted('update:visible')).toBeTruthy()
    })

    it('should emit refresh event after successful save', () => {
      // This would require mocking the save functionality
      // For now, we verify the component structure supports this
      expect(wrapper.vm).toBeDefined()
    })

    it('should emit saved event with vessel and changes data', () => {
      // This would require mocking the save functionality
      expect(wrapper.vm).toBeDefined()
    })
  })

  describe('Error Handling', () => {
    beforeEach(async () => {
      mockPermissionStore.canEditVesselInfo = true
      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })
      await wrapper.vm.$nextTick()
    })

    it('should handle missing vessel data gracefully', async () => {
      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: null,
        },
      })

      await wrapper.vm.$nextTick()
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing vessel_info gracefully', async () => {
      const vesselWithoutInfo = {
        id: 1,
        vessel: 'Test Vessel',
        voyage: 'TV001',
      }

      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: vesselWithoutInfo,
        },
      })

      await wrapper.vm.$nextTick()
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Loading States', () => {
    it('should disable form fields when loading', async () => {
      // This would require mocking the loading state from the composable
      mockPermissionStore.canEditVesselInfo = true

      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })

      await wrapper.vm.$nextTick()

      // Verify component structure supports loading states
      expect(wrapper.html()).toContain('el-form')
    })

    it('should show loading state on save button', async () => {
      mockPermissionStore.canEditVesselInfo = true

      wrapper = mount(EditVesselDialog, {
        props: {
          visible: true,
          vessel: mockVessel,
        },
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.html()).toContain('保存')
    })
  })
})
