import { describe, it, expect } from 'vitest'
import { parseDuration } from '@/utils/duration'

describe('duration utils', () => {
  describe('parseDuration', () => {
    it('parses hours and minutes correctly', () => {
      expect(parseDuration('1h30m')).toBe(5400) // 1h30m = 90min = 5400s
      expect(parseDuration('2h')).toBe(7200) // 2h = 7200s
      expect(parseDuration('45m')).toBe(2700) // 45m = 2700s
    })

    it('handles invalid formats gracefully', () => {
      expect(parseDuration('')).toBe(0)
      expect(parseDuration('invalid')).toBe(0)
      expect(parseDuration('1x30y')).toBe(0)
    })

    it('handles edge cases', () => {
      expect(parseDuration('0h0m')).toBe(0)
      expect(parseDuration('0h')).toBe(0)
      expect(parseDuration('0m')).toBe(0)
    })

    it('handles large numbers', () => {
      expect(parseDuration('24h')).toBe(86400) // 24h = 86400s
      expect(parseDuration('100h')).toBe(360000) // 100h = 360000s
    })
  })
}) 