export function parseDuration(duration: string): number {
  const matches = duration.match(/(\d+)h(\d+)m/)
  if (!matches) return 0
  const [_, hours, minutes] = matches
  return parseInt(hours) * 3600 + parseInt(minutes) * 60
} 