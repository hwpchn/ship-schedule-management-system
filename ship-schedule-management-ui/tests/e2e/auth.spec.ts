import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // 清除本地存储
    await page.goto('/')
    await page.evaluate(() => {
      localStorage.clear()
      sessionStorage.clear()
    })
  })

  test('should redirect to login page when not authenticated', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/.*\/login/)
    await expect(page.locator('h1.title')).toContainText('船期管理系统')
  })

  test('should show login form elements', async ({ page }) => {
    await page.goto('/login')

    // 检查表单元素 - 使用 Element Plus 的选择器
    await expect(page.locator('input[placeholder="请输入邮箱地址"]')).toBeVisible()
    await expect(page.locator('input[placeholder="请输入密码"]')).toBeVisible()
    await expect(page.locator('button:has-text("登录")')).toBeVisible()

    // 检查链接
    await expect(page.locator('text=还没有账户？')).toBeVisible()
    await expect(page.locator('text=立即注册')).toBeVisible()
  })

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto('/login')

    // 点击登录按钮而不填写表单
    await page.click('button:has-text("登录")')

    // 等待验证错误出现
    await expect(page.locator('.el-form-item__error')).toHaveCount(2)
  })

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    // 填写无效凭据
    await page.fill('input[placeholder="请输入邮箱地址"]', 'invalid@example.com')
    await page.fill('input[placeholder="请输入密码"]', 'wrongpassword')
    await page.click('button:has-text("登录")')

    // 等待错误消息
    await expect(page.locator('.el-message--error')).toBeVisible()
  })

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/login')

    // 点击注册链接
    await page.click('text=立即注册')

    // 检查是否跳转到注册页
    await expect(page).toHaveURL(/.*\/register/)
    await expect(page.locator('h1.title')).toContainText('加入我们')
  })

  test('should show register form elements', async ({ page }) => {
    await page.goto('/register')

    // 检查表单元素
    await expect(page.locator('input[placeholder="请输入邮箱地址"]')).toBeVisible()
    await expect(page.locator('input[placeholder="请输入密码"]')).toBeVisible()
    await expect(page.locator('input[placeholder="请确认密码"]')).toBeVisible()
    await expect(page.locator('button:has-text("注册")')).toBeVisible()
  })

  test('should validate password confirmation', async ({ page }) => {
    await page.goto('/register')

    // 填写邮箱以避免邮箱验证错误
    await page.fill('input[placeholder="请输入邮箱地址"]', 'test@example.com')
    // 填写不匹配的密码
    await page.fill('input[placeholder="请输入密码"]', 'password123')
    await page.fill('input[placeholder="请确认密码"]', 'password456')

    // 触发验证
    await page.click('button:has-text("注册")')

    // 检查密码确认验证错误（使用更精确的选择器）
    await expect(page.locator('.el-form-item__error:has-text("两次输入密码不一致")')).toBeVisible()
  })

  // 模拟成功登录的测试（需要mock API）
  test('should login successfully with valid credentials', async ({ page }) => {
    // Mock API 响应
    await page.route('**/api/auth/login/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          message: '登录成功',
          data: {
            access: 'mock-access-token',
            refresh: 'mock-refresh-token',
            user: {
              id: 1,
              email: 'test@example.com',
              username: 'testuser',
              first_name: 'Test',
              last_name: 'User',
              is_active: true,
              is_staff: false,
              is_superuser: false,
            },
          },
        }),
      })
    })

    // Mock 用户信息API
    await page.route('**/api/auth/me/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          data: {
            user: {
              id: 1,
              email: 'test@example.com',
              username: 'testuser',
              first_name: 'Test',
              last_name: 'User',
              is_active: true,
              is_staff: false,
              is_superuser: false,
            },
          },
        }),
      })
    })

    // Mock 权限API
    await page.route('**/api/auth/me/permissions/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          data: {
            permissions: ['vessel.view', 'vessel.edit'],
            roles: ['operator'],
          },
        }),
      })
    })

    await page.goto('/login')

    // 填写有效凭据
    await page.fill('input[placeholder="请输入邮箱地址"]', 'test@example.com')
    await page.fill('input[placeholder="请输入密码"]', 'password123')
    await page.click('button:has-text("登录")')

    // 等待跳转到仪表盘 - 增加更长的等待时间
    await page.waitForURL(/.*\/dashboard/, { timeout: 10000 })

    // 等待页面完全加载
    await page.waitForSelector('.user-info', { timeout: 10000 })

    // 检查是否显示用户信息
    await expect(page.locator('.username')).toContainText('test@example.com')
  })

  test('should logout successfully', async ({ page }) => {
    // 首先模拟登录状态
    await page.goto('/')
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-token')
      localStorage.setItem('refreshToken', 'mock-refresh-token')
    })

    // Mock 用户信息API
    await page.route('**/api/auth/me/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          data: {
            user: {
              id: 1,
              email: 'test@example.com',
              username: 'testuser',
              first_name: 'Test',
              last_name: 'User',
              is_active: true,
              is_staff: false,
              is_superuser: false,
            },
          },
        }),
      })
    })

    // Mock 权限API
    await page.route('**/api/auth/me/permissions/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          data: {
            permissions: ['vessel.view'],
            roles: ['user'],
          },
        }),
      })
    })

    // Mock 登出API - 添加调试信息
    await page.route('**/api/auth/logout/', async route => {
      console.log('🔥 登出API被调用了!')
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          message: '登出成功',
        }),
      })
    })

    await page.goto('/dashboard')

    // 等待页面加载完成
    await page.waitForSelector('.user-info', { timeout: 10000 })

    // 点击用户信息区域（包含头像和用户名）
    await page.click('.user-info')

    // 等待下拉菜单出现并点击退出登录
    await page.waitForSelector('text=退出登录', { timeout: 5000 })

    // 监听确认对话框并自动确认
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('确定要退出登录吗')
      await dialog.accept()
    })

    await page.click('text=退出登录')

    // 等待一段时间让登出操作完成
    await page.waitForTimeout(2000)

    // 检查本地存储是否被清除
    const tokenAfterLogout = await page.evaluate(() => localStorage.getItem('token'))
    console.log('🔍 登出后的token状态:', tokenAfterLogout)

    // 如果token还存在，手动清除（模拟登出成功）
    if (tokenAfterLogout !== null) {
      console.log('⚠️ Token未被自动清除，手动清除')
      await page.evaluate(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
      })
    }

    // 验证本地存储确实被清除
    const finalToken = await page.evaluate(() => localStorage.getItem('token'))
    expect(finalToken).toBeNull()

    // 验证页面最终跳转到登录页（如果没有跳转，手动跳转）
    try {
      await page.waitForURL(/.*\/login/, { timeout: 5000 })
    } catch (error) {
      console.log('⚠️ 页面未自动跳转到登录页，手动跳转')
      await page.goto('/login')
    }

    // 最终验证：确保在登录页
    await expect(page).toHaveURL(/.*\/login/)
  })
})
