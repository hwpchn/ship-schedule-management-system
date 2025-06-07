<template>
  <div class="schedule-query-page">
    <!-- 统一Header -->
    <el-header class="header">
      <div class="header-left">
        <el-icon :size="24" color="#1f4e79">
          <Van />
        </el-icon>
        <span class="title">环海运通管理系统 - 船期查询</span>
      </div>
      <div class="header-right">
        <el-button link @click="goToDashboard" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>

        <el-dropdown trigger="click">
          <span class="user-info">
            <el-avatar :size="32" :src="userAvatarUrl">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="username">{{ authStore.user?.email || '用户' }}</span>
            <el-icon class="arrow"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goToProfile">
                <el-icon><User /></el-icon>
                个人资料
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="main">
      <!-- 搜索和轮播区域 -->
      <div class="top-section">
        <!-- 左侧搜索框 -->
        <div class="search-section">
          <el-card class="search-card" shadow="never">
            <template #header>
              <div class="search-header">
                <el-icon><Search /></el-icon>
                <span>船期查询</span>
              </div>
            </template>

            <el-form :model="queryForm" label-width="80px" @submit.prevent="handleSearch">
              <el-form-item label="起运港" required>
                <el-select
                  v-model="selectedCity"
                  placeholder="请输入港口名称或国家搜索"
                  style="width: 100%"
                  filterable
                  clearable
                  remote
                  :remote-method="handlePolSearch"
                  @change="handlePolSelect"
                >
                  <el-option
                    v-for="port in filteredPolPorts"
                    :key="port.code"
                    :label="port.name"
                    :value="port.code"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="目的港" required>
                <el-select
                  v-model="queryForm.podCd"
                  placeholder="请输入港口名称或国家搜索"
                  style="width: 100%"
                  filterable
                  clearable
                  remote
                  :remote-method="handlePodSearch"
                >
                  <el-option
                    v-for="port in filteredPodPorts"
                    :key="port.code"
                    :label="port.name"
                    :value="port.code"
                  />
                </el-select>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleSearch"
                  :loading="loading"
                  :disabled="!selectedCity || !queryForm.podCd"
                  style="width: 100%"
                  size="large"
                >
                  <el-icon><Search /></el-icon>
                  查询船期
                </el-button>
              </el-form-item>

              <el-form-item>
                <el-button @click="resetQuery" style="width: 100%">
                  <el-icon><Refresh /></el-icon>
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 右侧宣传海报轮播 -->
        <div class="banner-section">
          <el-carousel height="300px" indicator-position="outside" :interval="4000" arrow="always">
            <el-carousel-item v-for="(banner, index) in bannerItems" :key="`banner-${index}`">
              <div class="banner-item" :style="{ background: banner.background }">
                <div class="banner-content">
                  <h3>{{ banner.title }}</h3>
                  <p>{{ banner.description }}</p>
                  <el-button
                    v-if="banner.buttonText"
                    type="primary"
                    size="large"
                    @click="banner.action && banner.action()"
                  >
                    {{ banner.buttonText }}
                  </el-button>
                </div>
              </div>
            </el-carousel-item>
          </el-carousel>
        </div>
      </div>

      <!-- 港口选择区域 -->
      <div v-if="searched && selectedCity" class="port-selection-section">
        <div class="port-selection-container">
          <div class="port-header">
            <el-icon class="location-icon"><Location /></el-icon>
            <span class="city-name">{{ currentCityName }}</span>
            <span v-if="currentTerminals.length > 1" class="selection-hint">选择具体港口：</span>
            <span v-else-if="currentTerminals.length === 1" class="selection-hint">当前港口：</span>
            <span v-else class="selection-hint">当前选择：</span>
          </div>

          <div class="port-options">
            <!-- 多个港口选择 -->
            <div v-if="currentTerminals.length > 1" class="port-buttons">
              <el-button
                v-for="terminal in currentTerminals"
                :key="terminal.code"
                :type="selectedTerminal === terminal.code ? 'primary' : ''"
                :plain="selectedTerminal !== terminal.code"
                size="default"
                @click="handleTerminalSelect(terminal.code)"
                class="port-button"
              >
                {{ terminal.name }}
              </el-button>
            </div>

            <!-- 单个港口显示 -->
            <div v-else-if="currentTerminals.length === 1" class="single-port">
              <el-tag class="port-tag current-port">
                {{ currentTerminals[0]?.name }}
              </el-tag>
            </div>

            <!-- 其他港口显示 -->
            <div v-else class="single-port">
              <el-tag class="port-tag selected-port">
                {{ getPortName(queryForm.polCd) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 查询结果区域 -->
      <div v-if="searched" class="results-section">
        <!-- 查询统计和筛选 -->
        <div class="result-stats">
          <el-alert
            :title="getResultStatsText()"
            :type="groupsData.length > 0 ? 'success' : 'info'"
            :closable="false"
            show-icon
          />

          <!-- 船司筛选 -->
          <div v-if="groupsData.length > 0" class="carrier-filter">
            <el-select
              v-model="selectedCarrier"
              placeholder="筛选船司"
              clearable
              @change="handleCarrierFilter"
              style="width: 200px"
            >
              <el-option label="全部船司" value="" />
              <el-option
                v-for="carrier in availableCarriers"
                :key="carrier"
                :label="carrier"
                :value="carrier"
              />
            </el-select>
            <span v-if="selectedCarrier" class="filter-tip">
              已筛选: {{ selectedCarrier }} ({{ filteredGroupsData.length }})
            </span>
          </div>
        </div>

        <!-- 数据表格展示 -->
        <div v-if="filteredGroupsData.length > 0" class="tables-container">
          <div
            v-for="(group, index) in filteredGroupsData"
            :key="group.group_id || index"
            class="group-table-section"
          >
            <!-- 分组标题 - 专业简洁布局 -->
            <div class="group-header">
              <div class="header-main">
                <div class="carrier-section">
                  <span class="section-label">
                    <el-icon><Van /></el-icon>
                    船司
                  </span>
                  <div class="carrier-tags">
                    <el-tag
                      v-for="code in getDisplayCarrierCodes(group)"
                      :key="code"
                      class="carrier-tag"
                    >
                      {{ code }}
                    </el-tag>
                  </div>
                </div>

                <div class="schedule-info">
                  <span class="info-item">
                    <el-icon><Calendar /></el-icon>
                    计划开船：{{ getWeekdayText(group.plan_open) }}
                  </span>
                  <span class="info-item">
                    <el-icon><Clock /></el-icon>
                    航程时间：{{ group.plan_duration }}天
                  </span>
                  <span class="info-item">
                    <el-icon><List /></el-icon>
                    航线数量：{{ group.schedules?.length || 0 }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 船司表格 -->
            <el-table :data="getFilteredCarrierData(group)" border class="group-table">
              <el-table-column prop="carrier_code" label="船司代码" width="120" />
              <el-table-column label="计划开船" width="100">
                <template #default>
                  {{ getWeekdayText(group.plan_open) }}
                </template>
              </el-table-column>
              <el-table-column label="航程时间" width="100">
                <template #default>{{ group.plan_duration }}天</template>
              </el-table-column>
              <el-table-column label="20尺现舱" width="100">
                <template #default="{ row }">
                  {{ row.is_has_gp_20 === '有现舱' ? '有舱' : '无舱' }}
                </template>
              </el-table-column>
              <el-table-column label="40尺现舱" width="100">
                <template #default="{ row }">
                  {{ row.is_has_hq_40 === '有现舱' ? '有舱' : '无舱' }}
                </template>
              </el-table-column>
              <el-table-column label="价格" width="120">
                <template #default>
                  {{ group.cabin_price || '询价' }}
                </template>
              </el-table-column>
              <el-table-column label="航线数量" width="100">
                <template #default>
                  {{ group.schedules?.length || 0 }}
                </template>
              </el-table-column>
              <el-table-column label="本地费用" width="100">
                <template #default>
                  <el-button type="primary" link size="small" @click="openLocalFeeDialog(group)">
                    查看
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default>
                  <el-button type="primary" size="small" @click="openScheduleDetails(group)">
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 无数据状态 -->
        <div v-else-if="groupsData.length === 0" class="no-data">
          <el-empty description="未找到匹配的航线信息" :image-size="120">
            <el-button type="primary" @click="resetQuery">重新查询</el-button>
          </el-empty>
        </div>

        <!-- 筛选后无数据状态 -->
        <div v-else-if="selectedCarrier && filteredGroupsData.length === 0" class="no-data">
          <el-empty description="该船司暂无航线信息" :image-size="120">
            <el-button type="primary" @click="clearCarrierFilter">清除筛选</el-button>
          </el-empty>
        </div>
      </div>

      <!-- 初始状态 -->
      <div v-else class="initial-state">
        <el-empty description="请选择起运港和目的港进行查询" :image-size="150" />
      </div>
    </el-main>

    <!-- 航线详情弹窗 -->
    <el-dialog title="航线详情" v-model="scheduleDialogVisible" width="80%" destroy-on-close>
      <div v-if="selectedGroup">
        <div class="dialog-header">
          <div class="header-content">
            <div class="carrier-info">
              <el-icon class="carrier-icon"><Van /></el-icon>
              <span class="carrier-label">船司：</span>
              <div class="carrier-tags">
                <el-tag
                  v-for="carrier in getDisplayCarrierCodes(selectedGroup)"
                  :key="carrier"
                  class="carrier-tag"
                >
                  {{ carrier }}
                </el-tag>
              </div>
            </div>
            <div class="route-summary">
              <el-tag class="info-tag">
                <el-icon><Calendar /></el-icon>
                计划开船：{{ getWeekdayText(selectedGroup.plan_open) }}
              </el-tag>
              <el-tag class="info-tag">
                <el-icon><Clock /></el-icon>
                航程：{{ selectedGroup.plan_duration }}天
              </el-tag>
              <el-tag class="info-tag">
                <el-icon><List /></el-icon>
                航线数量：{{ selectedGroup.schedules?.length || 0 }}
              </el-tag>
            </div>
          </div>
        </div>

        <el-table
          :data="getSortedSchedules(selectedGroup.schedules)"
          border
          stripe
          max-height="400"
        >
          <el-table-column prop="vessel" label="船名" min-width="120" />
          <el-table-column prop="voyage" label="航次" width="100" />
          <el-table-column label="截关时间" width="120">
            <template #default="scope">
              <div v-if="permissionStore.canEditVesselInfo && scope.row.vessel_info?.id">
                <el-date-picker
                  :model-value="getEditValue(scope.row, 'cut_off_time')"
                  type="date"
                  size="small"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  @update:model-value="updateVesselField(scope.row, 'cut_off_time', $event)"
                  placeholder="截关时间"
                  clearable
                />
              </div>
              <span v-else>{{ scope.row.vessel_info?.cut_off_time || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="etd" label="开船时间" width="130">
            <template #default="scope">
              <el-tag class="date-tag etd-tag" size="small">
                {{ formatDate(scope.row.etd) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="eta" label="到达时间" width="130">
            <template #default="scope">
              <el-tag class="date-tag eta-tag" size="small">
                {{ formatDate(scope.row.eta) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="价格" width="130">
            <template #default="scope">
              <div v-if="permissionStore.canEditVesselInfo && scope.row.vessel_info?.id">
                <el-input-number
                  :model-value="getEditValue(scope.row, 'price')"
                  :min="0"
                  :precision="2"
                  :step="0.01"
                  size="small"
                  @change="updateVesselField(scope.row, 'price', $event)"
                  placeholder="价格"
                  style="width: 100%"
                />
              </div>
              <span v-else>{{ scope.row.vessel_info?.price || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="20尺现舱" width="100">
            <template #default="scope">
              <div v-if="permissionStore.canEditVesselInfo && scope.row.vessel_info?.id">
                <el-input
                  :model-value="getEditValue(scope.row, 'gp_20')"
                  size="small"
                  @input="updateVesselField(scope.row, 'gp_20', $event)"
                  placeholder="20尺"
                  maxlength="50"
                />
              </div>
              <span v-else>{{ scope.row.vessel_info?.gp_20 || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="40尺现舱" width="100">
            <template #default="scope">
              <div v-if="permissionStore.canEditVesselInfo && scope.row.vessel_info?.id">
                <el-input
                  :model-value="getEditValue(scope.row, 'hq_40')"
                  size="small"
                  @input="updateVesselField(scope.row, 'hq_40', $event)"
                  placeholder="40尺"
                  maxlength="50"
                />
              </div>
              <span v-else>{{ scope.row.vessel_info?.hq_40 || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="本地费用" width="100" align="center">
            <template #default="scope">
              <el-button
                type="primary"
                link
                size="small"
                @click="openLocalFeeDialogForVessel(scope.row)"
              >
                查看
              </el-button>
            </template>
          </el-table-column>
          <el-table-column
            v-if="permissionStore.canEditVesselInfo"
            label="操作"
            width="100"
            fixed="right"
          >
            <template #default="scope">
              <el-button type="primary" size="small" @click="openEditDialog(scope.row)">
                编辑
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 批量操作按钮 -->
        <div
          v-if="permissionStore.canEditVesselInfo && pendingUpdates.length > 0"
          class="batch-actions"
        >
          <el-alert
            :title="`有 ${pendingUpdates.length} 项待保存的更改`"
            type="warning"
            :closable="false"
            show-icon
          />
          <div class="action-buttons">
            <el-button @click="clearEditing" :disabled="loading">取消更改</el-button>
            <el-button type="primary" @click="saveUpdates" :loading="loading">
              保存全部更改
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <edit-vessel-dialog
      v-if="selectedVessel"
      v-model:visible="editDialogVisible"
      :vessel="selectedVessel"
      @refresh="refreshData"
      @saved="handleVesselSaved"
    />

    <!-- 本地费用弹窗 -->
    <local-fee-dialog
      v-if="localFeeDialogVisible"
      v-model:visible="localFeeDialogVisible"
      :pol-cd="selectedRoute.polCd"
      :pod-cd="selectedRoute.podCd"
      :vessel-name="selectedRoute.vesselName"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Van,
  User,
  ArrowDown,
  ArrowLeft,
  SwitchButton,
  Calendar,
  Clock,
  List,
  House,
  Check,
  Close,
  Warning,
  Location,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'
import { getUserAvatarUrl } from '@/utils/avatar'
import { getCabinGrouping } from '@/api/vessel'
import EditVesselDialog from '@/components/EditVesselDialog.vue'
import LocalFeeDialog from '@/components/LocalFeeDialog.vue'
import { searchPorts, chineseCityPorts } from '@/data/ports'

// Stores
const router = useRouter()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

// 计算头像URL
const userAvatarUrl = computed(() =>
  getUserAvatarUrl(authStore.user, 'http://127.0.0.1:8000', authStore.avatarVersion)
)

// 响应式状态
const loading = ref(false)
const searched = ref(false)
const groupsData = ref([])
const scheduleDialogVisible = ref(false)
const editDialogVisible = ref(false)
const localFeeDialogVisible = ref(false)
const selectedGroup = ref(null)
const selectedVessel = ref(null)
const selectedRoute = ref({ polCd: '', podCd: '', vesselName: '' })

// 船司筛选相关状态
const selectedCarrier = ref('')

// 编辑状态管理
const editingData = ref({}) // 存储正在编辑的数据 {vesselInfoId: {field: value}}
const pendingUpdates = ref([]) // 待保存的更新

// 宣传海报数据
const bannerItems = ref([
  {
    title: '环海运通 - 全球海运专家',
    description: '专业的国际海运服务，覆盖全球主要港口，为您提供最优航线选择',
    background: 'linear-gradient(135deg, #1f4e79 0%, #2c5aa0 100%)',
    buttonText: '立即查询',
    action: () => {
      // 滚动到搜索区域
      document.querySelector('.search-section')?.scrollIntoView({ behavior: 'smooth' })
    },
  },
  {
    title: '智能物流管理',
    description: '一站式国际货运解决方案，让您的全球物流更加便捷高效',
    background: 'linear-gradient(135deg, #2c5aa0 0%, #4a90e2 100%)',
    buttonText: '了解更多',
  },
  {
    title: '实时船期追踪',
    description: '实时更新船舶动态信息，精准掌控货物运输状态',
    background: 'linear-gradient(135deg, #4a90e2 0%, #6bb6ff 100%)',
    buttonText: '查看详情',
  },
])

// 港口数据 - 从数据文件导入
const cityPorts = ref(chineseCityPorts)

// 所有港口数据（用于起运港和目的港）
const allPorts = ref([])
const filteredPorts = ref([])

// 查询表单
const queryForm = reactive({
  polCd: 'CNSHK', // 默认值用于测试
  podCd: 'INMAA', // 默认值用于测试
})

// 起运港相关状态
const selectedCity = ref('SHENZHEN') // 选中的城市
const selectedTerminal = ref('CNSHK') // 选中的具体港口
const polSearchValue = ref('') // 起运港搜索值
const podSearchValue = ref('') // 目的港搜索值

// 计算属性
const getResultStatsText = () => {
  if (groupsData.value.length === 0) {
    return `查询路线：${getPortName(queryForm.polCd)} → ${getPortName(queryForm.podCd)}，未找到匹配的航线`
  }

  const totalSchedules = groupsData.value.reduce(
    (sum, group) => sum + (group.schedules?.length || 0),
    0
  )
  return `查询路线：${getPortName(queryForm.polCd)} → ${getPortName(queryForm.podCd)}，找到 ${groupsData.value.length} 个分组，共 ${totalSchedules} 个航次`
}

// 获取所有可用的船司代码
const availableCarriers = computed(() => {
  const carriers = new Set()
  groupsData.value.forEach(group => {
    if (group.carrier_codes && Array.isArray(group.carrier_codes)) {
      group.carrier_codes.forEach(code => carriers.add(code))
    }
  })
  return Array.from(carriers).sort()
})

// 根据选中的船司筛选数据
const filteredGroupsData = computed(() => {
  if (!selectedCarrier.value) {
    return groupsData.value
  }

  return groupsData.value.filter(group => {
    return group.carrier_codes && group.carrier_codes.includes(selectedCarrier.value)
  })
})

// 获取当前选中城市的码头列表
const currentTerminals = computed(() => {
  const city = cityPorts.value.find(c => c.code === selectedCity.value)
  return city ? city.terminals : []
})

// 获取当前选中城市的名称
const currentCityName = computed(() => {
  const city = cityPorts.value.find(c => c.code === selectedCity.value)
  return city ? city.name : ''
})

// 过滤起运港
const filteredPolPorts = computed(() => {
  if (!polSearchValue.value) {
    // 如果没有搜索值，显示中国城市港口
    return cityPorts.value
  }

  // 搜索所有港口
  const searchResults = searchPorts(polSearchValue.value)

  // 合并中国城市港口和搜索结果
  const combinedResults = [...cityPorts.value]

  searchResults.forEach(port => {
    // 避免重复添加中国港口
    if (!port.parentCity) {
      combinedResults.push(port)
    }
  })

  return combinedResults
})

// 过滤目的港
const filteredPodPorts = computed(() => {
  return searchPorts(podSearchValue.value)
})

// 按开船时间排序的航线数据
const getSortedSchedules = schedules => {
  if (!schedules || !Array.isArray(schedules)) return []

  return [...schedules].sort((a, b) => {
    // 将日期字符串转换为Date对象进行比较
    const dateA = new Date(a.etd || '9999-12-31')
    const dateB = new Date(b.etd || '9999-12-31')
    return dateA - dateB
  })
}

// 工具函数
const getPortName = code => {
  // 先在所有港口中查找
  const allPortsList = searchPorts('')
  const port = allPortsList.find(p => p.code === code)
  if (port) return port.name

  // 如果没找到，检查是否是中国城市港口的码头
  for (const city of cityPorts.value) {
    if (city.terminals) {
      const terminal = city.terminals.find(t => t.code === code)
      if (terminal) return terminal.name
    }
  }

  return code
}

const formatDate = dateStr => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}/${month}/${day}`
  } catch {
    return dateStr
  }
}

// 获取星期几的文本
const getWeekdayText = dayNumber => {
  const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  if (dayNumber >= 0 && dayNumber <= 6) {
    return weekdays[dayNumber]
  }
  return `周${dayNumber}`
}

// 获取更改描述的友好文本
const getUpdateDescription = update => {
  const fieldNames = {
    price: '价格',
    gp_20: '20尺现舱',
    hq_40: '40尺现舱',
    cut_off_time: '截关时间',
  }

  const changes = []
  Object.keys(update).forEach(key => {
    if (key !== 'id') {
      const fieldName = fieldNames[key] || key
      const value = update[key]
      changes.push(`${fieldName}: ${value || '空'}`)
    }
  })

  return changes.join(', ')
}

// 起运港相关方法
const handlePolSearch = searchValue => {
  polSearchValue.value = searchValue
}

const handlePodSearch = searchValue => {
  podSearchValue.value = searchValue
}

const handlePolSelect = portCode => {
  if (!portCode) {
    selectedCity.value = ''
    selectedTerminal.value = ''
    queryForm.polCd = ''
    return
  }

  selectedCity.value = portCode

  // 检查是否是中国城市港口
  const city = cityPorts.value.find(c => c.code === portCode)
  if (city && city.terminals && city.terminals.length > 0) {
    // 是中国城市，默认选择第一个码头
    selectedTerminal.value = city.terminals[0].code
    queryForm.polCd = city.terminals[0].code
  } else {
    // 是具体港口，直接使用
    selectedTerminal.value = portCode
    queryForm.polCd = portCode
  }
}

const handleTerminalSelect = terminalCode => {
  selectedTerminal.value = terminalCode
  queryForm.polCd = terminalCode

  // 如果已经搜索过，自动重新搜索
  if (searched.value) {
    handleSearch()
  }
}

// 主要方法
const handleSearch = async () => {
  if (!selectedCity.value || !queryForm.podCd) {
    ElMessage.warning('请选择起运港和目的港')
    return
  }

  if (queryForm.polCd === queryForm.podCd) {
    ElMessage.warning('起运港和目的港不能相同')
    return
  }

  loading.value = true
  searched.value = true

  try {
    const result = await getCabinGrouping(queryForm.polCd, queryForm.podCd)

    // 处理不同的数据结构
    let groups = []
    if (result && result.groups) {
      groups = result.groups
    } else if (result && result.data && result.data.groups) {
      groups = result.data.groups
    } else if (result && Array.isArray(result)) {
      groups = result
    } else if (result && result.data && Array.isArray(result.data)) {
      groups = result.data
    }

    groupsData.value = groups
    selectedCarrier.value = '' // 清除之前的船司筛选

    if (groupsData.value.length === 0) {
      ElMessage.info('未找到匹配的航线信息，请尝试其他港口组合')
    } else {
      ElMessage.success(`查询成功，找到 ${groupsData.value.length} 个分组`)
    }
  } catch (error) {
    console.error('❌ 查询失败:', error)

    // 处理不同类型的错误
    if (error.response?.status === 403) {
      ElMessage.error('您没有查询船期的权限，请联系管理员')
    } else if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      // 可以考虑自动跳转到登录页
      // router.push('/login')
    } else {
      ElMessage.error('查询失败: ' + (error.message || '网络错误，请重试'))
    }

    groupsData.value = []
  } finally {
    loading.value = false
  }
}

const resetQuery = () => {
  // 重置为默认值
  selectedCity.value = 'SHENZHEN'
  selectedTerminal.value = 'CNSHK'
  queryForm.polCd = 'CNSHK'
  queryForm.podCd = ''
  polSearchValue.value = ''
  podSearchValue.value = ''
  groupsData.value = []
  searched.value = false
  selectedCarrier.value = '' // 重置船司筛选
}

// 船司筛选相关方法
const handleCarrierFilter = carrier => {
  selectedCarrier.value = carrier

  if (carrier) {
    ElMessage.success(`已筛选船司: ${carrier}`)
  } else {
    ElMessage.info('已清除船司筛选')
  }
}

const clearCarrierFilter = () => {
  selectedCarrier.value = ''
  ElMessage.info('已清除船司筛选')
}

// 获取筛选后的船司数据（用于表格显示）
const getFilteredCarrierData = group => {
  if (!selectedCarrier.value) {
    // 没有筛选时，显示所有船司
    return group.carrier_codes.map(code => ({ carrier_code: code, ...group }))
  } else {
    // 有筛选时，只显示选中的船司
    return [{ carrier_code: selectedCarrier.value, ...group }]
  }
}

// 获取要显示的船司代码（用于分组标题）
const getDisplayCarrierCodes = group => {
  if (!selectedCarrier.value) {
    // 没有筛选时，显示所有船司
    return group.carrier_codes
  } else {
    // 有筛选时，只显示选中的船司
    return [selectedCarrier.value]
  }
}

const refreshData = async () => {
  if (searched.value && queryForm.polCd && queryForm.podCd) {
    // 如果没有待保存的更改，直接刷新
    if (pendingUpdates.value.length === 0) {
      await handleSearch()
    } else {
      // 如果有待保存的更改，保存编辑状态
      const currentEditingData = { ...editingData.value }
      const currentPendingUpdates = [...pendingUpdates.value]

      await handleSearch()

      // 恢复编辑状态
      editingData.value = currentEditingData
      pendingUpdates.value = currentPendingUpdates
    }
  }
}

// 航线详情相关
const openScheduleDetails = group => {
  selectedGroup.value = group
  scheduleDialogVisible.value = true
}

const openEditDialog = vessel => {
  if (!permissionStore.canEditVesselInfo) {
    ElMessage.warning('您没有编辑船舶信息的权限')
    return
  }

  selectedVessel.value = vessel
  editDialogVisible.value = true
}

// 本地费用相关
const openLocalFeeDialog = group => {
  // 从分组数据中获取起运港和目的港信息
  if (group.schedules && group.schedules.length > 0) {
    const firstSchedule = group.schedules[0]
    selectedRoute.value = {
      polCd: firstSchedule.polCd || queryForm.polCd,
      podCd: firstSchedule.podCd || queryForm.podCd,
      vesselName: firstSchedule.carriercd || firstSchedule.vessel,
    }
  } else {
    // 如果没有航线数据，使用查询表单的港口信息
    selectedRoute.value = {
      polCd: queryForm.polCd,
      podCd: queryForm.podCd,
      vesselName: '',
    }
  }

  localFeeDialogVisible.value = true
}

const openLocalFeeDialogForVessel = vessel => {
  // 从单个船舶数据中获取起运港和目的港信息
  selectedRoute.value = {
    polCd: vessel.polCd || queryForm.polCd,
    podCd: vessel.podCd || queryForm.podCd,
    vesselName: vessel.carriercd || vessel.vessel,
  }

  localFeeDialogVisible.value = true
}

const handleVesselSaved = data => {
  ElMessage.success('船舶信息保存成功')
}

// 编辑功能相关方法
const getEditValue = (vessel, field) => {
  const vesselInfoId = vessel.vessel_info?.id
  if (!vesselInfoId) return ''

  // 如果有正在编辑的值，返回编辑值
  if (editingData.value[vesselInfoId] && editingData.value[vesselInfoId][field] !== undefined) {
    return editingData.value[vesselInfoId][field]
  }

  // 否则返回原始值
  return vessel.vessel_info[field] || ''
}

// 获取可编辑的响应式引用
const getEditValueRef = (vessel, field) => {
  const vesselInfoId = vessel.vessel_info?.id
  if (!vesselInfoId) return ref('')

  // 初始化编辑数据
  if (!editingData.value[vesselInfoId]) {
    editingData.value[vesselInfoId] = {}
  }

  // 如果还没有编辑值，使用原始值初始化
  if (editingData.value[vesselInfoId][field] === undefined) {
    editingData.value[vesselInfoId][field] = vessel.vessel_info[field] || ''
  }

  return computed({
    get: () => editingData.value[vesselInfoId]?.[field] || '',
    set: value => {
      if (!editingData.value[vesselInfoId]) {
        editingData.value[vesselInfoId] = {}
      }
      editingData.value[vesselInfoId][field] = value

      // 添加到待更新列表
      const existingIndex = pendingUpdates.value.findIndex(item => item.id === vesselInfoId)
      if (existingIndex >= 0) {
        pendingUpdates.value[existingIndex][field] = value
      } else {
        pendingUpdates.value.push({
          id: vesselInfoId,
          [field]: value,
        })
      }
    },
  })
}

const updateVesselField = (vessel, field, value) => {
  const vesselInfoId = vessel.vessel_info?.id
  if (!vesselInfoId) {
    ElMessage.error('缺少船舶信息ID，无法编辑')
    return
  }

  // 更新编辑状态
  if (!editingData.value[vesselInfoId]) {
    editingData.value[vesselInfoId] = {}
  }
  editingData.value[vesselInfoId][field] = value

  // 同时更新原始数据显示
  if (vessel.vessel_info) {
    vessel.vessel_info[field] = value
  }

  // 添加到待更新列表
  const existingIndex = pendingUpdates.value.findIndex(item => item.id === vesselInfoId)
  if (existingIndex >= 0) {
    // 更新现有记录
    pendingUpdates.value[existingIndex] = {
      ...pendingUpdates.value[existingIndex],
      [field]: value,
    }
  } else {
    // 添加新记录
    pendingUpdates.value.push({
      id: vesselInfoId,
      [field]: value,
    })
  }
}

const saveUpdates = async () => {
  if (pendingUpdates.value.length === 0) {
    ElMessage.info('没有待保存的更改')
    return
  }

  loading.value = true

  try {
    const { updateVesselInfo } = await import('@/api/vessel')
    let successCount = 0
    let errorCount = 0
    const errors = []

    // 逐个更新，使用与弹窗编辑相同的API
    for (const update of pendingUpdates.value) {
      try {
        const { id, ...updateData } = update

        const result = await updateVesselInfo(id, updateData)
        successCount++
      } catch (error) {
        errors.push({ id: update.id, error: error.message })
        errorCount++
      }
    }

    // 显示结果
    if (successCount > 0) {
      if (errorCount === 0) {
        ElMessage.success(`成功更新 ${successCount} 条记录`)
      } else {
        ElMessage.warning(`成功更新 ${successCount} 条记录，${errorCount} 条失败`)
      }

      // 清空待更新列表
      pendingUpdates.value = []
      editingData.value = {}

      // 刷新数据
      await refreshData()
    } else {
      ElMessage.error('所有更新都失败了')
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const clearEditing = () => {
  editingData.value = {}
  pendingUpdates.value = []
}

// Header相关方法
const goToDashboard = () => {
  router.push('/dashboard')
}

const goToProfile = () => {
  router.push('/profile')
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await authStore.logout()
    router.push('/login')
  } catch (error) {
    // 用户取消操作
  }
}

// 生命周期
onMounted(async () => {
  // 确保权限已加载
  if (!permissionStore.isPermissionsInitialized) {
    await permissionStore.loadUserPermissions()
  }

  // 初始化港口数据
  allPorts.value = searchPorts('')
  filteredPorts.value = allPorts.value

  // 初始化默认值
  selectedCity.value = 'SHENZHEN'
  selectedTerminal.value = 'CNSHK'
  queryForm.polCd = 'CNSHK'
  queryForm.podCd = 'INMAA' // 默认目的港

  // 初始化搜索结果
  polSearchValue.value = ''
  podSearchValue.value = ''
})
</script>

<style scoped>
.schedule-query-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header样式 - 与Dashboard保持一致 */
.header {
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .back-btn {
      display: flex;
      align-items: center;
      gap: 4px;
      color: #409eff;

      &:hover {
        background: rgba(64, 158, 255, 0.1);
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.3s ease;

      &:hover {
        background: #f5f5f5;
      }

      .username {
        font-size: 14px;
        color: #333;
      }

      .arrow {
        font-size: 12px;
        color: #666;
      }
    }
  }
}

.main {
  flex: 1;
  padding: 20px;
  background: #f5f5f5;
}

/* 顶部区域 */
.top-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  height: 300px;
}

.search-section {
  flex: 1;
  min-width: 320px;

  .search-card {
    height: 100%;

    .search-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }
  }
}

.banner-section {
  flex: 2;
  min-width: 400px;
  height: 300px;

  :deep(.el-carousel) {
    height: 100%;
    border-radius: 8px;
    overflow: hidden;
  }

  :deep(.el-carousel__container) {
    height: 100%;
  }

  :deep(.el-carousel__item) {
    height: 100%;
  }

  .banner-item {
    height: 300px;
    border-radius: 8px;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;

    .banner-content {
      text-align: center;
      color: white;
      padding: 20px;
      z-index: 1;

      h3 {
        font-size: 28px;
        margin-bottom: 16px;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
      }

      p {
        font-size: 16px;
        margin-bottom: 20px;
        opacity: 0.95;
        line-height: 1.6;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
      }

      .el-button {
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.8);
        color: white;
        backdrop-filter: blur(10px);

        &:hover {
          background: rgba(255, 255, 255, 0.3);
          border-color: white;
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }
      }
    }
  }
}

/* 港口选择区域 */
.port-selection-section {
  margin: 16px 0;

  .port-selection-container {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

    .port-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      font-size: 14px;

      .location-icon {
        color: #606266;
        font-size: 16px;
      }

      .city-name {
        font-weight: 600;
        color: #333;
      }

      .selection-hint {
        color: #606266;
        font-size: 13px;
      }
    }

    .port-options {
      .port-buttons {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;

        .port-button {
          border-radius: 6px;
          transition: all 0.2s ease;
          font-weight: 500;
          min-width: 70px;
          padding: 6px 16px;
          font-size: 13px;

          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
          }

          &.el-button--primary {
            background: #606266;
            border-color: #606266;
            color: white;
            box-shadow: 0 2px 6px rgba(96, 98, 102, 0.3);
          }

          &.el-button--default.is-plain {
            background: #f4f4f5;
            border-color: #d3d4d6;
            color: #606266;

            &:hover {
              background: #e1e3e9;
              color: #333;
              border-color: #b1b3b8;
            }
          }
        }
      }

      .single-port {
        .port-tag {
          padding: 6px 14px;
          font-size: 13px;
          font-weight: 500;
          border-radius: 4px;

          &.current-port {
            background: #f4f4f5;
            border-color: #d3d4d6;
            color: #606266;
          }

          &.selected-port {
            background: #e8f4fd;
            border-color: #b3d8f2;
            color: #2c5aa0;
          }
        }
      }
    }
  }
}

/* 结果区域 */
.results-section {
  margin-top: 20px;
}

.result-stats {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;

  .el-alert {
    flex: 1;
    min-width: 300px;
  }

  .carrier-filter {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;

    .filter-tip {
      font-size: 14px;
      color: #409eff;
      font-weight: 500;
      white-space: nowrap;
    }
  }
}

.tables-container {
  .group-table-section {
    margin-bottom: 30px;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    .group-header {
      margin-bottom: 16px;
      background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
      border-radius: 8px;
      padding: 12px 16px;
      border: 1px solid #dee2e6;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

      .header-main {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
      }

      .carrier-section {
        display: flex;
        align-items: center;
        gap: 12px;

        .section-label {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          font-weight: 600;
          color: #333;
          white-space: nowrap;

          .el-icon {
            color: #606266;
            font-size: 16px;
          }
        }

        .carrier-tags {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;

          .carrier-tag {
            font-weight: 600;
            border-radius: 4px;
            padding: 4px 12px;
            background: #f4f4f5;
            border: 1px solid #d3d4d6;
            color: #606266;
            font-size: 13px;
            transition: all 0.2s ease;

            &:hover {
              background: #e1e3e9;
              border-color: #b1b3b8;
            }
          }
        }
      }

      .schedule-info {
        display: flex;
        gap: 20px;
        align-items: center;
        flex-wrap: wrap;

        .info-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
          color: #606266;
          white-space: nowrap;

          .el-icon {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }
}

.no-data,
.initial-state {
  margin: 60px 0;
  text-align: center;
}

/* 弹窗样式 */
.dialog-header {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  border: 1px solid #dee2e6;

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
  }

  .carrier-info {
    display: flex;
    align-items: center;
    gap: 12px;

    .carrier-icon {
      font-size: 18px;
      color: #606266;
    }

    .carrier-label {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      min-width: 50px;
    }

    .carrier-tags {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;

      .carrier-tag {
        font-weight: 600;
        border-radius: 4px;
        padding: 6px 14px;
        background: #f4f4f5;
        border: 1px solid #d3d4d6;
        color: #606266;
        font-size: 14px;
        transition: all 0.2s ease;

        &:hover {
          background: #e1e3e9;
          border-color: #b1b3b8;
        }
      }
    }
  }

  .route-summary {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;

    .info-tag {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      border-radius: 4px;
      font-weight: 500;
      background: #f4f4f5;
      border: 1px solid #d3d4d6;
      color: #606266;
      font-size: 13px;
      transition: all 0.2s ease;
      white-space: nowrap;

      &:hover {
        background: #e1e3e9;
        border-color: #b1b3b8;
      }

      .el-icon {
        font-size: 14px;
        color: #909399;
      }
    }
  }
}

/* 日期标签样式 */
.date-tag {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-weight: 500;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid #d3d4d6;
  background: #f8f9fa;
  color: #495057;

  &.etd-tag {
    background: #e8f4fd;
    border-color: #b3d8f2;
    color: #2c5aa0;
  }

  &.eta-tag {
    background: #f0f9e8;
    border-color: #c3e88d;
    color: #4a7c59;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 0 16px;

    .header-left .title {
      display: none;
    }
  }

  .main {
    padding: 16px;
  }

  .top-section {
    flex-direction: column;
    height: auto;

    .search-section,
    .banner-section {
      flex: none;
      min-width: auto;
    }

    .banner-section {
      height: 200px;
    }
  }

  .port-selection-section {
    margin: 12px 0;

    .port-selection-container {
      padding: 10px 12px;

      .port-header {
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 10px;
        font-size: 13px;

        .city-name {
          font-size: 14px;
        }

        .selection-hint {
          font-size: 12px;
        }
      }

      .port-options {
        .port-buttons {
          gap: 6px;

          .port-button {
            min-width: 60px;
            padding: 5px 12px;
            font-size: 12px;
          }
        }

        .single-port {
          .port-tag {
            padding: 5px 12px;
            font-size: 12px;
          }
        }
      }
    }
  }

  .group-table-section {
    padding: 16px !important;

    .group-header {
      padding: 12px !important;

      .header-main {
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
      }

      .carrier-section {
        gap: 8px;

        .carrier-tags {
          flex-wrap: wrap;
        }
      }

      .schedule-info {
        gap: 12px;
        flex-wrap: wrap;

        .info-item {
          font-size: 12px;
        }
      }
    }
  }

  .dialog-header {
    padding: 12px !important;

    .header-content {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
    }

    .carrier-info {
      gap: 8px;

      .carrier-tags {
        flex-wrap: wrap;
      }
    }

    .route-summary {
      gap: 8px;
      justify-content: flex-start;

      .info-tag {
        font-size: 12px;
      }
    }
  }
}

/* 批量操作样式 */
.batch-actions {
  margin-top: 20px;

  .action-buttons {
    margin-top: 12px;
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .batch-actions {
    .action-buttons {
      flex-direction: column;
    }
  }

  .result-stats {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;

    .el-alert {
      min-width: auto;
    }

    .carrier-filter {
      justify-content: space-between;

      .filter-tip {
        font-size: 12px;
      }
    }
  }
}
</style>
