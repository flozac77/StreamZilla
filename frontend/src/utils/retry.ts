export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error | null = null
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      console.warn(`Attempt ${i + 1} failed:`, error)
      
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }
  
  throw lastError
} 