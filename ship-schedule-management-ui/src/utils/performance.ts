// 性能优化工具

// 防抖函数
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate = false
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }
    
    const callNow = immediate && !timeout
    
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    
    if (callNow) func(...args)
  }
}

// 节流函数
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean

  return function executedFunction(this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// 图片懒加载
export class LazyImageLoader {
  private observer: IntersectionObserver | null = null
  
  constructor() {
    if ('IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement
              const src = img.dataset.src
              
              if (src) {
                img.src = src
                img.removeAttribute('data-src')
                this.observer?.unobserve(img)
              }
            }
          })
        },
        {
          rootMargin: '50px 0px',
          threshold: 0.01
        }
      )
    }
  }
  
  observe(element: HTMLImageElement) {
    if (this.observer) {
      this.observer.observe(element)
    }
  }
  
  disconnect() {
    if (this.observer) {
      this.observer.disconnect()
    }
  }
}

// 虚拟滚动
export interface VirtualScrollItem {
  id: string | number
  height: number
  data: any
}

export class VirtualScroll {
  private container: HTMLElement
  private itemHeight: number
  private visibleCount: number
  private scrollTop = 0
  private startIndex = 0
  private endIndex = 0
  
  constructor(
    container: HTMLElement,
    itemHeight: number,
    visibleCount: number
  ) {
    this.container = container
    this.itemHeight = itemHeight
    this.visibleCount = visibleCount
    
    this.container.addEventListener('scroll', this.handleScroll.bind(this))
  }
  
  private handleScroll() {
    this.scrollTop = this.container.scrollTop
    this.startIndex = Math.floor(this.scrollTop / this.itemHeight)
    this.endIndex = Math.min(
      this.startIndex + this.visibleCount,
      this.getTotalCount()
    )
  }
  
  getVisibleRange() {
    return {
      start: this.startIndex,
      end: this.endIndex
    }
  }
  
  private getTotalCount() {
    // 需要外部提供总数
    return 0
  }
}

// 内存管理
export class MemoryManager {
  private cache = new Map<string, any>()
  private maxSize: number
  
  constructor(maxSize = 100) {
    this.maxSize = maxSize
  }
  
  set(key: string, value: any) {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value
      if (firstKey !== undefined) {
        this.cache.delete(firstKey)
      }
    }
    this.cache.set(key, value)
  }
  
  get(key: string) {
    return this.cache.get(key)
  }
  
  has(key: string) {
    return this.cache.has(key)
  }
  
  clear() {
    this.cache.clear()
  }
  
  size() {
    return this.cache.size
  }
}

// 性能监控
export class PerformanceMonitor {
  private marks = new Map<string, number>()
  
  mark(name: string) {
    this.marks.set(name, performance.now())
  }
  
  measure(name: string, startMark: string, endMark?: string) {
    const start = this.marks.get(startMark)
    const end = endMark ? this.marks.get(endMark) : performance.now()
    
    if (start && end) {
      const duration = end - start
      console.log(`Performance [${name}]: ${duration.toFixed(2)}ms`)
      return duration
    }
    
    return 0
  }
  
  // 监控页面加载性能
  getPageLoadMetrics() {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    
    return {
      // DNS 查询时间
      dnsLookup: navigation.domainLookupEnd - navigation.domainLookupStart,
      // TCP 连接时间
      tcpConnect: navigation.connectEnd - navigation.connectStart,
      // 请求响应时间
      request: navigation.responseEnd - navigation.requestStart,
      // DOM 解析时间
      domParse: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      // 页面加载完成时间
      pageLoad: navigation.loadEventEnd - navigation.loadEventStart,
      // 首次内容绘制
      fcp: this.getFCP(),
      // 最大内容绘制
      lcp: this.getLCP()
    }
  }
  
  private getFCP() {
    const entries = performance.getEntriesByType('paint')
    const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint')
    return fcpEntry ? fcpEntry.startTime : 0
  }
  
  private getLCP() {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1]
        resolve(lastEntry.startTime)
      }).observe({ entryTypes: ['largest-contentful-paint'] })
    })
  }
}

// 资源预加载
export class ResourcePreloader {
  private loadedResources = new Set<string>()
  
  preloadImage(src: string): Promise<void> {
    if (this.loadedResources.has(src)) {
      return Promise.resolve()
    }
    
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        this.loadedResources.add(src)
        resolve()
      }
      img.onerror = reject
      img.src = src
    })
  }
  
  preloadImages(srcs: string[]): Promise<void[]> {
    return Promise.all(srcs.map(src => this.preloadImage(src)))
  }
  
  preloadScript(src: string): Promise<void> {
    if (this.loadedResources.has(src)) {
      return Promise.resolve()
    }
    
    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.onload = () => {
        this.loadedResources.add(src)
        resolve()
      }
      script.onerror = reject
      script.src = src
      document.head.appendChild(script)
    })
  }
}

// 单例实例
export const lazyImageLoader = new LazyImageLoader()
export const memoryManager = new MemoryManager()
export const performanceMonitor = new PerformanceMonitor()
export const resourcePreloader = new ResourcePreloader()
