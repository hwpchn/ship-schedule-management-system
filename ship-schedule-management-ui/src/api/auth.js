import request from './request'

export const authApi = {
  // 用户注册
  register(data) {
    return request({
      url: '/auth/register/',
      method: 'post',
      data: {
        email: data.email,
        password: data.password,
        password_confirm: data.confirmPassword,
      },
    })
  },

  // 用户登录
  login(data) {
    return request({
      url: '/auth/login/',
      method: 'post',
      data: {
        email: data.email,
        password: data.password,
      },
    })
  },

  // 用户登出
  logout() {
    return request({
      url: '/auth/logout/',
      method: 'post',
    })
  },

  // 获取用户信息
  getUserInfo() {
    return request({
      url: '/auth/user/',
      method: 'get',
    })
  },

  // 获取简化用户信息
  getMe() {
    return request({
      url: '/auth/me/',
      method: 'get',
    })
  },

  // 获取当前用户权限
  getUserPermissions() {
    return request({
      url: '/auth/me/permissions/',
      method: 'get',
    })
  },

  // 更新用户信息
  updateUser(data) {
    return request({
      url: '/auth/user/',
      method: 'patch',
      data,
    })
  },

  // 刷新JWT令牌
  refreshToken(data) {
    return request({
      url: '/auth/token/refresh/',
      method: 'post',
      data,
    })
  },

  // 获取用户列表
  getUsers(params = {}) {
    return request({
      url: '/auth/users/',
      method: 'get',
      params,
    })
  },

  // 获取权限列表
  getPermissions() {
    return request({
      url: '/auth/permissions/',
      method: 'get',
    })
  },

  // 获取角色列表
  getRoles(params = {}) {
    return request({
      url: '/auth/roles/',
      method: 'get',
      params,
    })
  },

  // 获取角色详情
  getRoleDetail(roleId) {
    return request({
      url: `/auth/roles/${roleId}/`,
      method: 'get',
    })
  },

  // 创建角色
  createRole(data) {
    return request({
      url: '/auth/roles/',
      method: 'post',
      data,
    })
  },

  // 更新角色
  updateRole(roleId, data) {
    return request({
      url: `/auth/roles/${roleId}/`,
      method: 'put',
      data,
    })
  },

  // 删除角色
  deleteRole(roleId) {
    return request({
      url: `/auth/roles/${roleId}/`,
      method: 'delete',
    })
  },

  // 获取用户角色
  getUserRoles(userId) {
    return request({
      url: `/auth/users/${userId}/roles/`,
      method: 'get',
    })
  },

  // 分配用户角色
  assignUserRoles(userId, roles) {
    return request({
      url: `/auth/users/${userId}/roles/`,
      method: 'post',
      data: { roles },
    })
  },

  // 更新用户角色
  updateUserRoles(userId, roles) {
    return request({
      url: `/auth/users/${userId}/roles/`,
      method: 'put',
      data: { roles },
    })
  },

  // 移除用户角色
  removeUserRole(userId, roleId) {
    return request({
      url: `/auth/users/${userId}/roles/${roleId}/`,
      method: 'delete',
    })
  },

  // 创建用户
  createUser(data) {
    return request({
      url: '/auth/users-management/',
      method: 'post',
      data: {
        email: data.email,
        password: data.password,
        password_confirm: data.password_confirm,
        first_name: data.first_name,
        last_name: data.last_name,
      },
    })
  },

  // 获取用户详情
  getUserDetail(userId) {
    return request({
      url: `/auth/users-management/${userId}/`,
      method: 'get',
    })
  },

  // 更新用户信息
  updateUserInfo(userId, data) {
    return request({
      url: `/auth/users-management/${userId}/`,
      method: 'put',
      data,
    })
  },

  // 删除用户
  deleteUser(userId) {
    return request({
      url: `/auth/users-management/${userId}/`,
      method: 'delete',
    })
  },

  // 上传用户头像
  uploadAvatar(file) {
    const formData = new FormData()
    formData.append('avatar', file)

    return request({
      url: '/auth/me/avatar/',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 删除用户头像
  deleteAvatar() {
    return request({
      url: '/auth/me/avatar/',
      method: 'delete',
    })
  },
}
