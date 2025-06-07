/**
 * 头像URL处理工具函数
 */

/**
 * 获取完整的头像URL
 * @param {string} avatarPath - 头像路径（可能是相对路径或完整URL）
 * @param {string} baseURL - 后端服务器基础URL，默认为空字符串（使用代理）
 * @param {boolean} addTimestamp - 是否添加时间戳避免缓存，默认为true
 * @returns {string|null} 完整的头像URL或null
 */
export function getFullAvatarUrl(avatarPath, baseURL = '', addTimestamp = true) {
  if (!avatarPath) return null

  let fullURL

  // 如果是完整URL，直接使用
  if (avatarPath.startsWith('http://') || avatarPath.startsWith('https://')) {
    fullURL = avatarPath
  } else {
    // 如果是相对路径，拼接基础URL
    if (baseURL) {
      fullURL = avatarPath.startsWith('/') ? `${baseURL}${avatarPath}` : `${baseURL}/${avatarPath}`
    } else {
      // 如果没有baseURL，直接使用相对路径（通过代理访问）
      fullURL = avatarPath.startsWith('/') ? avatarPath : `/${avatarPath}`
    }
  }

  // 添加时间戳避免浏览器缓存
  if (addTimestamp) {
    const separator = fullURL.includes('?') ? '&' : '?'
    fullURL = `${fullURL}${separator}t=${Date.now()}`
  }

  return fullURL
}

/**
 * 从用户对象中获取头像URL
 * @param {object} user - 用户对象
 * @param {string} baseURL - 后端服务器基础URL，默认为空字符串（使用代理）
 * @param {number} version - 版本号，用于强制刷新缓存
 * @returns {string|null} 完整的头像URL或null
 */
export function getUserAvatarUrl(user, baseURL = '', version = null) {
  if (!user) return null

  // 优先使用 avatar_url，其次使用 avatar
  const avatarPath = user.avatar_url || user.avatar

  if (!avatarPath) return null

  let fullURL = getFullAvatarUrl(avatarPath, baseURL, false) // 先不添加时间戳

  // 如果提供了版本号，使用版本号而不是时间戳
  if (version) {
    const separator = fullURL.includes('?') ? '&' : '?'
    fullURL = `${fullURL}${separator}v=${version}`
  } else {
    // 如果没有版本号，添加时间戳
    const separator = fullURL.includes('?') ? '&' : '?'
    fullURL = `${fullURL}${separator}t=${Date.now()}`
  }

  return fullURL
}
