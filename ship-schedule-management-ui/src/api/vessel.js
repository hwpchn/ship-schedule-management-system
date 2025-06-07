import request from './request'

/**
 * 船舶信息相关API
 */
export const vesselApi = {
  /**
   * 获取舱位分组信息
   * @param {string} polCd 起运港代码
   * @param {string} podCd 目的港代码
   * @returns {Promise} API响应
   */
  getCabinGrouping: (polCd, podCd) => {
    return request({
      url: '/schedules/cabin-grouping-with-info/',
      method: 'GET',
      params: { polCd, podCd },
    })
  },

  /**
   * 根据schedule_id获取vessel_info的ID
   * @param {number} scheduleId 航班ID
   * @returns {Promise} API响应
   */
  getVesselInfoBySchedule: scheduleId => {
    return request({
      url: '/vessel-info/',
      method: 'GET',
      params: { schedule_id: scheduleId },
    })
  },

  /**
   * 更新船舶信息
   * @param {number} vesselInfoId 船舶信息ID
   * @param {Object} updateData 更新数据
   * @returns {Promise} API响应
   */
  updateVesselInfo: (vesselInfoId, updateData) => {
    // 验证只更新允许的字段
    const allowedFields = ['price', 'gp_20', 'hq_40', 'cut_off_time']
    const validData = {}

    allowedFields.forEach(field => {
      if (Object.prototype.hasOwnProperty.call(updateData, field)) {
        validData[field] = updateData[field]
      }
    })

    return request({
      url: `/vessel-info/${vesselInfoId}/`,
      method: 'PATCH',
      data: validData,
    })
  },

  /**
   * 批量更新船舶信息
   * @param {Array} updates 批量更新数据
   * @returns {Promise} API响应
   */
  batchUpdateVesselInfo: updates => {
    const allowedFields = ['price', 'gp_20', 'hq_40', 'cut_off_time']

    // 预处理更新数据，确保只更新可编辑字段
    const validUpdates = updates.map(item => {
      const validFields = {}
      allowedFields.forEach(field => {
        if (item[field] !== undefined) {
          validFields[field] = item[field]
        }
      })
      return {
        id: item.id,
        ...validFields,
      }
    })

    return request({
      url: '/vessel-info/bulk-update/',
      method: 'POST',
      data: { updates: validUpdates },
    })
  },
}

/**
 * 获取vessel_info的ID (便捷方法)
 * @param {number} scheduleId 航班ID
 * @returns {Promise<number|null>} vessel_info的ID
 */
export const getVesselInfoId = async scheduleId => {
  try {
    const response = await vesselApi.getVesselInfoBySchedule(scheduleId)
    if (response.code === 200 && response.data.results?.length > 0) {
      return response.data.results[0].id
    }
    return null
  } catch (error) {
    console.error('获取vessel_info ID失败:', error)
    throw error
  }
}

/**
 * 更新船舶信息 (便捷方法)
 * @param {number} vesselInfoId 船舶信息ID
 * @param {Object} updateData 更新数据
 * @returns {Promise} 更新结果
 */
export const updateVesselInfo = async (vesselInfoId, updateData) => {
  try {
    const response = await vesselApi.updateVesselInfo(vesselInfoId, updateData)
    if (response.code === 200) {
      return response.data
    }
    throw new Error(response.message || '更新失败')
  } catch (error) {
    console.error('更新船舶信息失败:', error)
    throw error
  }
}

/**
 * 获取舱位分组信息 (便捷方法)
 * @param {string} polCd 起运港代码
 * @param {string} podCd 目的港代码
 * @returns {Promise} 分组数据
 */
export const getCabinGrouping = async (polCd, podCd) => {
  try {
    const response = await vesselApi.getCabinGrouping(polCd, podCd)
    if (response.code === 200) {
      return response.data
    }
    throw new Error(response.message || '查询失败')
  } catch (error) {
    console.error('获取舱位分组信息失败:', error)
    throw error
  }
}
