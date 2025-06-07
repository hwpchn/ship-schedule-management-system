<template>
  <el-dialog
    title="编辑船舶信息"
    v-model="dialogVisible"
    width="600px"
    :before-close="handleClose"
    destroy-on-close
  >
    <!-- 权限检查加载状态 -->
    <div v-if="!permissionStore.isPermissionsInitialized" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 主要内容区域 -->
    <div v-else>
      <!-- 有编辑权限的用户界面 -->
      <div v-if="permissionStore.canEditVesselInfo">
        <el-alert
          title="您可以编辑以下船舶信息字段"
          type="info"
          :closable="false"
          show-icon
          class="mb-4"
        />

        <!-- 编辑表单 -->
        <el-form ref="formRef" :model="form" label-width="120px" :rules="formRules" @submit.prevent>
          <!-- 价格字段 -->
          <el-form-item label="价格" prop="price">
            <el-input-number
              v-model="form.price"
              :min="0"
              :precision="2"
              :step="0.01"
              placeholder="请输入价格"
              style="width: 100%"
              :disabled="loading"
            />
            <div class="field-help">单位：人民币元</div>
          </el-form-item>

          <!-- 20尺普柜现舱字段 -->
          <el-form-item label="20尺普柜现舱" prop="gp_20">
            <el-input
              v-model="form.gp_20"
              placeholder="请输入20尺普柜现舱信息"
              :disabled="loading"
              maxlength="50"
              show-word-limit
            />
            <div class="field-help">当前舱位可用情况</div>
          </el-form-item>

          <!-- 40尺高柜现舱字段 -->
          <el-form-item label="40尺高柜现舱" prop="hq_40">
            <el-input
              v-model="form.hq_40"
              placeholder="请输入40尺高柜现舱信息"
              :disabled="loading"
              maxlength="50"
              show-word-limit
            />
            <div class="field-help">当前舱位可用情况</div>
          </el-form-item>

          <!-- 截关时间字段 -->
          <el-form-item label="截关时间" prop="cut_off_time">
            <el-date-picker
              v-model="form.cut_off_time"
              type="date"
              placeholder="选择截关日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
              :disabled="loading"
              :disabled-date="disabledDate"
            />
            <div class="field-help">货物截关的最后日期</div>
          </el-form-item>
        </el-form>

        <!-- 变更提示 -->
        <el-alert
          v-if="hasChanges"
          title="检测到数据变更，请记得保存修改"
          type="warning"
          :closable="false"
          show-icon
          class="mt-4"
        />

        <!-- 错误信息显示 -->
        <el-alert
          v-if="editErrors.general"
          :title="editErrors.general"
          type="error"
          :closable="false"
          show-icon
          class="mt-4"
        />
      </div>

      <!-- 无编辑权限的用户界面（只读视图） -->
      <div v-else>
        <el-alert
          title="您没有编辑权限，仅可查看船舶信息"
          type="warning"
          :closable="false"
          show-icon
          class="mb-4"
        />

        <div class="read-only-view">
          <div class="info-item">
            <span class="label">价格:</span>
            <span class="value">
              {{ vessel?.vessel_info?.price ? `¥${vessel.vessel_info.price}` : '未设置' }}
            </span>
          </div>

          <div class="info-item">
            <span class="label">20尺普柜现舱:</span>
            <span class="value">{{ vessel?.vessel_info?.gp_20 || '暂无信息' }}</span>
          </div>

          <div class="info-item">
            <span class="label">40尺高柜现舱:</span>
            <span class="value">{{ vessel?.vessel_info?.hq_40 || '暂无信息' }}</span>
          </div>

          <div class="info-item">
            <span class="label">截关时间:</span>
            <span class="value">{{ vessel?.vessel_info?.cut_off_time || '暂无信息' }}</span>
          </div>

          <!-- 船舶基本信息 -->
          <el-divider content-position="left">船舶基本信息</el-divider>

          <div class="info-item">
            <span class="label">船名:</span>
            <span class="value">{{ vessel?.vessel || '未知' }}</span>
          </div>

          <div class="info-item">
            <span class="label">航次:</span>
            <span class="value">{{ vessel?.voyage || '未知' }}</span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <!-- 有编辑权限时的按钮 -->
        <template v-if="permissionStore.canEditVesselInfo">
          <el-button @click="handleCancel" :disabled="loading">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="loading" :disabled="!hasChanges">
            保存修改
          </el-button>
        </template>

        <!-- 无编辑权限时的按钮 -->
        <template v-else>
          <el-button @click="dialogVisible = false">关闭</el-button>
        </template>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePermissionStore } from '@/stores/permission'
import { useVesselEdit, useVesselForm } from '@/composables/useVesselEdit'

// Props
const props = defineProps({
  vessel: {
    type: Object,
    default: () => null,
  },
  visible: {
    type: Boolean,
    default: false,
  },
})

// Emits
const emit = defineEmits(['update:visible', 'refresh', 'saved'])

// Stores and Composables
const permissionStore = usePermissionStore()
const { editVesselInfo, loading, errors: editErrors } = useVesselEdit()

// 响应式状态
const dialogVisible = ref(props.visible)
const formRef = ref()

// 初始化表单数据
const initialFormData = computed(() => ({
  price: props.vessel?.vessel_info?.price || 0,
  gp_20: props.vessel?.vessel_info?.gp_20 || '',
  hq_40: props.vessel?.vessel_info?.hq_40 || '',
  cut_off_time: props.vessel?.vessel_info?.cut_off_time || '',
}))

// 使用表单组合式函数
const { form, resetForm, updateOriginalData, hasChanges, getChanges, validateForm } = useVesselForm(
  initialFormData.value
)

// 表单验证规则
const formRules = {
  price: [{ type: 'number', min: 0, message: '价格不能为负数', trigger: 'blur' }],
  cut_off_time: [
    {
      validator: (rule, value, callback) => {
        if (value) {
          const date = new Date(value)
          if (isNaN(date.getTime())) {
            callback(new Error('请选择有效的日期'))
          }
        }
        callback()
      },
      trigger: 'change',
    },
  ],
}

// 监听props变化
watch(
  () => props.visible,
  val => {
    dialogVisible.value = val
    if (val && props.vessel) {
      // 重置表单数据
      updateOriginalData(initialFormData.value)
    }
  }
)

watch(dialogVisible, val => {
  emit('update:visible', val)
})

// 禁用过去的日期
const disabledDate = time => {
  return time.getTime() < Date.now() - 8.64e7 // 禁用昨天之前的日期
}

// 处理保存
const handleSave = async () => {
  if (!formRef.value) return

  try {
    // 表单验证
    const valid = await formRef.value.validate()
    if (!valid) return

    // 自定义验证
    const { valid: customValid, errors } = validateForm()
    if (!customValid) {
      const firstError = Object.values(errors)[0]
      ElMessage.error(firstError)
      return
    }

    // 检查是否有变更
    if (!hasChanges.value) {
      ElMessage.info('没有数据变更')
      return
    }

    // 获取vessel_info ID
    const vesselInfoId = props.vessel?.vessel_info?.id
    if (!vesselInfoId) {
      ElMessage.error('缺少船舶信息ID，无法保存')
      return
    }

    // 保存变更
    const changes = getChanges()
    const success = await editVesselInfo(vesselInfoId, changes)

    if (success) {
      // 更新原始数据
      updateOriginalData(form)

      // 通知父组件
      emit('saved', { vessel: props.vessel, changes })
      emit('refresh')

      // 关闭对话框
      dialogVisible.value = false
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  }
}

// 处理取消
const handleCancel = () => {
  if (hasChanges.value) {
    ElMessageBox.confirm('检测到未保存的修改，确定要放弃这些修改吗？', '确认取消', {
      confirmButtonText: '确定',
      cancelButtonText: '继续编辑',
      type: 'warning',
    })
      .then(() => {
        resetForm()
        dialogVisible.value = false
      })
      .catch(() => {
        // 用户选择继续编辑，不做任何操作
      })
  } else {
    dialogVisible.value = false
  }
}

// 处理对话框关闭
const handleClose = done => {
  if (hasChanges.value) {
    ElMessageBox.confirm('检测到未保存的修改，确定要关闭吗？', '确认关闭', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
      .then(() => {
        resetForm()
        done()
      })
      .catch(() => {
        // 用户取消，不关闭对话框
      })
  } else {
    done()
  }
}

// 确保权限已加载
watch(
  () => props.visible,
  async visible => {
    if (visible && !permissionStore.isPermissionsInitialized) {
      await permissionStore.loadUserPermissions()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.loading-container {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 16px;
}

.mt-4 {
  margin-top: 16px;
}

.field-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.read-only-view {
  margin-top: 20px;
}

.info-item {
  margin: 12px 0;
  display: flex;
  align-items: center;
}

.label {
  width: 120px;
  color: #606266;
  font-weight: 500;
}

.value {
  flex: 1;
  color: #303133;
  font-weight: 400;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__content) {
  flex-direction: column;
  align-items: flex-start;
}
</style>
