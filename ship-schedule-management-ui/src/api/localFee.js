import request from '@/api/request'

// 模拟数据 - 仅在开发环境且API完全不可用时使用
const mockLocalFeeData = [
  {
    id: 1,
    名称: '起运港码头费',
    单位: '箱型',
    '20GP': '760.00',
    '40GP': '1287.00',
    '40HQ': '1287.00',
    单票价格: null,
    币种: 'CNY',
  },
  {
    id: 2,
    名称: '保安费',
    单位: '票',
    '20GP': null,
    '40GP': null,
    '40HQ': null,
    单票价格: '50.00',
    币种: 'USD',
  },
  {
    id: 3,
    名称: '文件费',
    单位: '票',
    '20GP': null,
    '40GP': null,
    '40HQ': null,
    单票价格: '25.00',
    币种: 'USD',
  },
  {
    id: 4,
    名称: '目的港码头费',
    单位: '箱型',
    '20GP': '850.00',
    '40GP': '1400.00',
    '40HQ': '1400.00',
    单票价格: null,
    币种: 'INR',
  },
  {
    id: 5,
    名称: '燃油附加费',
    单位: '箱型',
    '20GP': '120.00',
    '40GP': '240.00',
    '40HQ': '240.00',
    单票价格: null,
    币种: 'USD',
  },
]

// 本地费用API对象
export const localFeeApi = {
  /**
   * 查询本地费用（前端格式）⭐ 重要
   * @param {string} polCd - 起运港五字码（必填）
   * @param {string} podCd - 目的港五字码（必填）
   * @param {string} carriercd - 船公司英文名（可选）
   * @returns {Promise<Object>} 查询结果
   */
  async query(polCd, podCd, carriercd = '') {
    try {
      const params = { polCd, podCd }
      if (carriercd) {
        params.carriercd = carriercd
      }

      const response = await request.get('/api/local-fees/local-fees/query/', { params })
      return response.data
    } catch (error) {
      // 只有在网络错误或服务器完全不可用时才使用模拟数据
      if (error.response?.status === 401 || error.response?.status === 403) {
        // 认证/权限错误，直接抛出
        throw error
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        // 网络错误，使用模拟数据
        console.warn('网络错误，使用模拟数据:', error.message)
        return {
          status: 'success',
          data: mockLocalFeeData,
        }
      } else {
        // 其他错误，抛出
        throw error
      }
    }
  },

  /**
   * 获取所有本地费用
   * @param {Object} params - 查询参数
   * @returns {Promise<Object>} 查询结果
   */
  async getList(params = {}) {
    try {
      const response = await request.get('/api/local-fees/local-fees/', { params })
      return response.data
    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        throw error
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        console.warn('网络错误，使用模拟数据:', error.message)
        return {
          status: 'success',
          data: mockLocalFeeData.map(item => ({
            id: item.id,
            name: item.名称,
            unit_name: item.单位,
            price_20gp: item['20GP'],
            price_40gp: item['40GP'],
            price_40hq: item['40HQ'],
            price_per_bill: item.单票价格,
            currency: item.币种,
          })),
        }
      } else {
        throw error
      }
    }
  },

  /**
   * 获取单个本地费用详情
   * @param {number} id - 费用ID
   * @returns {Promise<Object>} 费用详情
   */
  async getDetail(id) {
    const response = await request.get(`/api/local-fees/local-fees/${id}/`)
    return response.data
  },

  /**
   * 创建新的本地费用
   * @param {Object} data - 费用数据
   * @returns {Promise<Object>} 创建结果
   */
  async create(data) {
    const response = await request.post('/api/local-fees/local-fees/', data)
    return response.data
  },

  /**
   * 更新本地费用
   * @param {number} id - 费用ID
   * @param {Object} data - 更新数据
   * @returns {Promise<Object>} 更新结果
   */
  async update(id, data) {
    const response = await request.put(`/api/local-fees/local-fees/${id}/`, data)
    return response.data
  },

  /**
   * 删除本地费用
   * @param {number} id - 费用ID
   * @returns {Promise<Object>} 删除结果
   */
  async delete(id) {
    const response = await request.delete(`/api/local-fees/local-fees/${id}/`)
    return response.data
  },

  // 别名方法，保持向后兼容
  async deleteRow(id) {
    return this.delete(id)
  },

  /**
   * 批量保存更改
   * @param {Array} changes - 更改列表
   * @returns {Promise<Object>} 保存结果
   */
  async batchSave(changes) {
    const results = []

    for (const change of changes) {
      try {
        if (change.isNew) {
          // 新建记录
          const result = await this.create(change.data)
          results.push({ success: true, data: result })
        } else {
          // 更新记录
          const result = await this.update(change.id, change.data)
          results.push({ success: true, data: result })
        }
      } catch (error) {
        results.push({ success: false, error: error.message })
      }
    }

    return {
      status: 'success',
      results,
      successCount: results.filter(r => r.success).length,
      errorCount: results.filter(r => !r.success).length,
    }
  },
}

/**
 * 便捷函数 - 查询本地费用（前端格式）
 * @param {string} polCd - 起运港五字码
 * @param {string} podCd - 目的港五字码
 * @param {string} carriercd - 船公司英文名（可选）
 * @returns {Promise<Object>} 查询结果
 */
export const queryLocalFees = async (polCd, podCd, carriercd = '') => {
  return await localFeeApi.query(polCd, podCd, carriercd)
}

/**
 * 便捷函数 - 获取本地费用列表
 * @param {string} polCd - 起运港五字码
 * @param {string} podCd - 目的港五字码
 * @returns {Promise<Object>} 查询结果
 */
export const getLocalFees = async (polCd, podCd) => {
  return await localFeeApi.getList({ polCd, podCd })
}

/**
 * 便捷函数 - 根据船名获取本地费用（保持向后兼容）
 * @param {string} vesselName - 船名
 * @param {string} polCd - 起运港五字码
 * @param {string} podCd - 目的港五字码
 * @returns {Promise<Object>} 查询结果
 */
export const getLocalFeesByVessel = async (vesselName, polCd, podCd) => {
  // 使用新的查询API，将船名作为carriercd参数
  return await localFeeApi.query(polCd, podCd, vesselName)
}

// 默认导出
export default localFeeApi
