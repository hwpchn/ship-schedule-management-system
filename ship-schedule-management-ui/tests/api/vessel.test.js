import { describe, it, expect, vi, beforeEach } from 'vitest'
import { vesselApi, getVesselInfoId, updateVesselInfo, getCabinGrouping } from '@/api/vessel'
import request from '@/api/request'

// Mock request module
vi.mock('@/api/request')

describe('Vessel API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('vesselApi.getCabinGrouping', () => {
    it('should get cabin grouping successfully', async () => {
      const mockResponse = {
        code: 200,
        data: {
          groups: [
            {
              id: 1,
              vessel_name: 'Test Vessel',
              voyage: 'TV001',
              departure_port: 'CNSHA',
              arrival_port: 'USLAX',
              etd: '2024-01-15',
              eta: '2024-02-01',
            },
          ],
        },
      }

      request.mockResolvedValue(mockResponse)

      const result = await vesselApi.getCabinGrouping('CNSHA', 'USLAX')

      expect(request).toHaveBeenCalledWith({
        url: '/schedules/cabin-grouping-with-info/',
        method: 'GET',
        params: { polCd: 'CNSHA', podCd: 'USLAX' },
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle API error', async () => {
      const mockError = new Error('Network error')
      request.mockRejectedValue(mockError)

      await expect(vesselApi.getCabinGrouping('CNSHA', 'USLAX')).rejects.toThrow('Network error')
    })
  })

  describe('vesselApi.getVesselInfoBySchedule', () => {
    it('should get vessel info by schedule id successfully', async () => {
      const mockResponse = {
        code: 200,
        data: {
          results: [
            {
              id: 1,
              schedule_id: 123,
              price: 1500,
              gp_20: 100,
              hq_40: 50,
              cut_off_time: '2024-01-10T12:00:00Z',
            },
          ],
        },
      }

      request.mockResolvedValue(mockResponse)

      const result = await vesselApi.getVesselInfoBySchedule(123)

      expect(request).toHaveBeenCalledWith({
        url: '/vessel-info/',
        method: 'GET',
        params: { schedule_id: 123 },
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle vessel not found', async () => {
      const mockError = new Error('Vessel not found')
      request.mockRejectedValue(mockError)

      await expect(vesselApi.getVesselInfoBySchedule(999)).rejects.toThrow('Vessel not found')
    })
  })

  describe('vesselApi.updateVesselInfo', () => {
    it('should update vessel info successfully', async () => {
      const mockResponse = {
        code: 200,
        data: {
          id: 1,
          price: 1600,
          gp_20: 120,
          hq_40: 60,
          cut_off_time: '2024-01-10T15:00:00Z',
        },
      }

      request.mockResolvedValue(mockResponse)

      const updateData = {
        price: 1600,
        gp_20: 120,
        hq_40: 60,
        cut_off_time: '2024-01-10T15:00:00Z',
      }

      const result = await vesselApi.updateVesselInfo(1, updateData)

      expect(request).toHaveBeenCalledWith({
        url: '/vessel-info/1/',
        method: 'PATCH',
        data: updateData,
      })
      expect(result).toEqual(mockResponse)
    })

    it('should filter out non-allowed fields', async () => {
      const mockResponse = {
        code: 200,
        data: { id: 1, price: 1600 },
      }

      request.mockResolvedValue(mockResponse)

      const updateData = {
        price: 1600,
        vessel_name: 'Should be filtered', // Not allowed
        id: 999, // Not allowed
      }

      await vesselApi.updateVesselInfo(1, updateData)

      expect(request).toHaveBeenCalledWith({
        url: '/vessel-info/1/',
        method: 'PATCH',
        data: { price: 1600 }, // Only allowed fields
      })
    })

    it('should handle update validation errors', async () => {
      const mockError = new Error('Invalid price value')
      request.mockRejectedValue(mockError)

      const updateData = { price: -100 }

      await expect(vesselApi.updateVesselInfo(1, updateData)).rejects.toThrow('Invalid price value')
    })
  })

  describe('vesselApi.batchUpdateVesselInfo', () => {
    it('should batch update vessel info successfully', async () => {
      const mockResponse = {
        code: 200,
        data: {
          updated_count: 2,
          results: [
            { id: 1, price: 1600 },
            { id: 2, price: 1700 },
          ],
        },
      }

      request.mockResolvedValue(mockResponse)

      const updates = [
        { id: 1, price: 1600, vessel_name: 'Should be filtered' },
        { id: 2, price: 1700, gp_20: 100 },
      ]

      const result = await vesselApi.batchUpdateVesselInfo(updates)

      expect(request).toHaveBeenCalledWith({
        url: '/vessel-info/bulk-update/',
        method: 'POST',
        data: {
          updates: [
            { id: 1, price: 1600 },
            { id: 2, price: 1700, gp_20: 100 },
          ],
        },
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getVesselInfoId (convenience function)', () => {
    it('should get vessel info id successfully', async () => {
      const mockResponse = {
        code: 200,
        data: {
          results: [{ id: 123, schedule_id: 456 }],
        },
      }

      request.mockResolvedValue(mockResponse)

      const result = await getVesselInfoId(456)

      expect(result).toBe(123)
    })

    it('should return null when no results', async () => {
      const mockResponse = {
        code: 200,
        data: { results: [] },
      }

      request.mockResolvedValue(mockResponse)

      const result = await getVesselInfoId(999)

      expect(result).toBeNull()
    })

    it('should handle API error', async () => {
      const mockError = new Error('API Error')
      request.mockRejectedValue(mockError)

      await expect(getVesselInfoId(456)).rejects.toThrow('API Error')
    })
  })

  describe('updateVesselInfo (convenience function)', () => {
    it('should update vessel info successfully', async () => {
      const mockResponse = {
        code: 200,
        data: { id: 1, price: 1600 },
      }

      request.mockResolvedValue(mockResponse)

      const updateData = { price: 1600 }
      const result = await updateVesselInfo(1, updateData)

      expect(result).toEqual({ id: 1, price: 1600 })
    })

    it('should handle update failure', async () => {
      const mockResponse = {
        code: 400,
        message: '更新失败',
      }

      request.mockResolvedValue(mockResponse)

      const updateData = { price: 1600 }

      await expect(updateVesselInfo(1, updateData)).rejects.toThrow('更新失败')
    })
  })

  describe('getCabinGrouping (convenience function)', () => {
    it('should get cabin grouping successfully', async () => {
      const mockResponse = {
        code: 200,
        data: { groups: [] },
      }

      request.mockResolvedValue(mockResponse)

      const result = await getCabinGrouping('CNSHA', 'USLAX')

      expect(result).toEqual({ groups: [] })
    })

    it('should handle query failure', async () => {
      const mockResponse = {
        code: 400,
        message: '查询失败',
      }

      request.mockResolvedValue(mockResponse)

      await expect(getCabinGrouping('CNSHA', 'USLAX')).rejects.toThrow('查询失败')
    })
  })
})
