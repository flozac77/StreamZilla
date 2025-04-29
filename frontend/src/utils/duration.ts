export function parseDuration(duration: string): number {
  if (!duration) return 0
  
  const hoursMatch = duration.match(/(\d+)h/)
  const minutesMatch = duration.match(/(\d+)m/)
  
  const hours = hoursMatch ? parseInt(hoursMatch[1]) : 0
  const minutes = minutesMatch ? parseInt(minutesMatch[1]) : 0
  
  return hours * 3600 + minutes * 60
} 