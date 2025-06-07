import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getVesselInfoId, updateVesselInfo, vesselApi } from '@/api/vessel'
import { usePermissionStore } from '@/stores/permission'

/**
 * 船舶信息编辑Composable
 */
export function useVesselEdit() {
  const permissionStore = usePermissionStore()
  const loading = ref(false)
  const errors = ref({})

  // 可编辑字段定义
  const EDITABLE_FIELDS = ['price', 'gp_20', 'hq_40', 'cut_off_time']

  /**
   * 验证字段是否可编辑
   * @param {string} fieldName 字段名
   * @returns {boolean} 是否可编辑
   */
  const isFieldEditable = fieldName => {
    return EDITABLE_FIELDS.includes(fieldName)
  }

  /**
   * 编辑单个船舶信息字段
   * @param {number} scheduleId 航班ID
   * @param {string} fieldName 字段名
   * @param {any} newValue 新值
   * @returns {Promise<boolean>} 是否编辑成功
   */
  const editSingleField = async (scheduleId, fieldName, newValue) => {
    // 权限检查
    if (!permissionStore.hasPermission('vessel_info.update')) {
      ElMessage.error('您没有编辑船舶信息的权限')
      return false
    }

    // 字段验证
    if (!isFieldEditable(fieldName)) {
      ElMessage.error(`不支持编辑字段: ${fieldName}`)
      return false
    }

    loading.value = true
    errors.value = {}

    try {
      // 获取vessel_info ID
      const vesselInfoId = await getVesselInfoId(scheduleId)

      if (!vesselInfoId) {
        throw new Error('未找到对应的船舶信息记录')
      }

      // 构造更新数据
      const updateData = { [fieldName]: newValue }

      // 调用更新API
      await updateVesselInfo(vesselInfoId, updateData)

      ElMessage.success('更新成功')
      return true
    } catch (error) {
      console.error('编辑失败:', error)
      const errorMessage = error.message || '编辑失败'
      errors.value[fieldName] = errorMessage
      ElMessage.error(errorMessage)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 批量编辑船舶信息
   * @param {Object} vesselInfoId 船舶信息ID
   * @param {Object} updateData 更新数据
   * @returns {Promise<boolean>} 是否编辑成功
   */
  const editVesselInfo = async (vesselInfoId, updateData) => {
    // 权限检查
    if (!permissionStore.hasPermission('vessel_info.update')) {
      ElMessage.error('您没有编辑船舶信息的权限')
      return false
    }

    loading.value = true
    errors.value = {}

    try {
      // 过滤只包含可编辑字段
      const validData = {}
      Object.keys(updateData).forEach(key => {
        if (isFieldEditable(key) && updateData[key] !== undefined) {
          validData[key] = updateData[key]
        }
      })

      if (Object.keys(validData).length === 0) {
        throw new Error('没有可更新的字段')
      }

      // 调用更新API
      await updateVesselInfo(vesselInfoId, validData)

      ElMessage.success('保存成功')
      return true
    } catch (error) {
      console.error('保存失败:', error)
      const errorMessage = error.message || '保存失败'
      errors.value.general = errorMessage
      ElMessage.error(errorMessage)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 批量更新多个船舶信息
   * @param {Array} updates 更新数据数组
   * @returns {Promise<boolean>} 是否更新成功
   */
  const batchUpdateVesselInfo = async updates => {
    // 权限检查
    if (!permissionStore.hasPermission('vessel_info.update')) {
      ElMessage.error('您没有批量编辑船舶信息的权限')
      return false
    }

    loading.value = true
    errors.value = {}

    try {
      await vesselApi.batchUpdateVesselInfo(updates)
      ElMessage.success('批量更新成功')
      return true
    } catch (error) {
      console.error('批量更新失败:', error)
      const errorMessage = error.message || '批量更新失败'
      errors.value.batch = errorMessage
      ElMessage.error(errorMessage)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置错误状态
   */
  const resetErrors = () => {
    errors.value = {}
  }

  /**
   * 检查用户是否有编辑权限
   * @returns {boolean} 是否有编辑权限
   */
  const canEdit = () => {
    return permissionStore.hasPermission('vessel_info.update')
  }

  return {
    // 状态
    loading,
    errors,

    // 常量
    EDITABLE_FIELDS,

    // 方法
    isFieldEditable,
    editSingleField,
    editVesselInfo,
    batchUpdateVesselInfo,
    resetErrors,
    canEdit,
  }
}

/**
 * 船舶信息表单Composable
 */
export function useVesselForm(initialData = {}) {
  // 表单数据
  const form = reactive({
    price: initialData.price || 0,
    gp_20: initialData.gp_20 || '',
    hq_40: initialData.hq_40 || '',
    cut_off_time: initialData.cut_off_time || '',
  })

  // 原始数据备份
  const originalData = reactive({ ...form })

  /**
   * 重置表单到原始数据
   */
  const resetForm = () => {
    Object.keys(originalData).forEach(key => {
      form[key] = originalData[key]
    })
  }

  /**
   * 更新原始数据
   * @param {Object} newData 新数据
   */
  const updateOriginalData = newData => {
    Object.keys(newData).forEach(key => {
      if (Object.prototype.hasOwnProperty.call(form, key)) {
        originalData[key] = newData[key]
        form[key] = newData[key]
      }
    })
  }

  /**
   * 检查表单是否有变化
   * @returns {ComputedRef<boolean>} 是否有变化
   */
  const hasChanges = computed(() => {
    return Object.keys(form).some(key => form[key] !== originalData[key])
  })

  /**
   * 获取变更的字段
   * @returns {Object} 变更的字段数据
   */
  const getChanges = () => {
    const changes = {}
    Object.keys(form).forEach(key => {
      if (form[key] !== originalData[key]) {
        changes[key] = form[key]
      }
    })
    return changes
  }

  /**
   * 验证表单数据
   * @returns {Object} 验证结果 { valid: boolean, errors: Object }
   */
  const validateForm = () => {
    const errors = {}

    // 价格验证
    if (form.price !== null && form.price !== undefined) {
      if (form.price < 0) {
        errors.price = '价格不能为负数'
      }
    }

    // 截关时间验证
    if (form.cut_off_time) {
      const cutOffDate = new Date(form.cut_off_time)
      if (isNaN(cutOffDate.getTime())) {
        errors.cut_off_time = '截关时间格式不正确'
      }
    }

    return {
      valid: Object.keys(errors).length === 0,
      errors,
    }
  }

  return {
    // 状态
    form,
    originalData,

    // 方法
    resetForm,
    updateOriginalData,
    hasChanges,
    getChanges,
    validateForm,
  }
}
