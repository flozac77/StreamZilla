export function parseDuration(durationStr: string): number {
  if (!durationStr) return 0;

  let totalSeconds = 0;
  // Regex to capture optional hours (h), minutes (m), and seconds (s)
  // It allows for formats like "1h23m45s", "30m10s", "2h", "50s", "1h45s", etc.
  const durationRegex = /(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?/;
  const matches = durationStr.match(durationRegex);

  if (matches) {
    // parseInt will correctly interpret the captured digits.
    // If a group is not matched (e.g., no 'h' part), it will be undefined,
    // and parseInt(undefined) results in NaN, so we use a fallback to 0.
    const hours = matches[1] ? parseInt(matches[1], 10) : 0;
    const minutes = matches[2] ? parseInt(matches[2], 10) : 0;
    const seconds = matches[3] ? parseInt(matches[3], 10) : 0;
    
    totalSeconds = (hours * 3600) + (minutes * 60) + seconds;
  }
  
  // If the regex doesn't match at all (e.g. "PT1H2M3S" or invalid format), 
  // and if totalSeconds is still 0, we might consider a fallback for ISO 8601 PT format
  // For now, the requirement focuses on "XhYmZs" as suggested by VideoListView.vue
  // and the API's own example "3m21s".
  // The current regex will parse "1h23m45s" but not "PT1H23M45S" because of the "PT".
  // If "PT" is present, matches will be null, and 0 will be returned.

  return totalSeconds;
}