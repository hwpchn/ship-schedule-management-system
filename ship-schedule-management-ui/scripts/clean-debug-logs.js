#!/usr/bin/env node

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// 需要清理的文件模式
// const patterns = [
//   /console\.log\(/g,
//   /console\.warn\(/g,
//   /console\.error\(/g,
//   /console\.info\(/g,
//   /console\.debug\(/g,
// ]

// 替换映射
const replacements = {
  'console.log(': 'routerLogger.debug(',
  'console.warn(': 'routerLogger.warn(',
  'console.error(': 'routerLogger.error(',
  'console.info(': 'routerLogger.info(',
  'console.debug(': 'routerLogger.debug(',
}

// 需要处理的文件
const filesToProcess = [path.join(__dirname, '../src/router/index.js')]

function cleanFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`文件不存在: ${filePath}`)
    return
  }

  let content = fs.readFileSync(filePath, 'utf8')
  let modified = false

  // 应用替换
  for (const [search, replace] of Object.entries(replacements)) {
    if (content.includes(search)) {
      content = content.replaceAll(search, replace)
      modified = true
    }
  }

  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8')
    console.log(`已清理: ${filePath}`)
  } else {
    console.log(`无需清理: ${filePath}`)
  }
}

// 处理所有文件
console.log('开始清理调试日志...')
filesToProcess.forEach(cleanFile)
console.log('清理完成!')
