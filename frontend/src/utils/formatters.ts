export const formatViews = (views: number): string => {
  if (views >= 1000000) {
    return `${(views / 1000000).toFixed(1)}M`;
  } else if (views >= 1000) {
    return `${(views / 1000).toFixed(1)}k`;
  }
  return views.toString();
};

export const formatDurationForDisplay = (duration: string): string => {
  const matches = duration.match(/(\d+h)?(\d+m)?(\d+s)?/);
  if (!matches) return duration;
  
  const hours = matches[1] ? matches[1].replace('h', '') : '0';
  const minutes = matches[2] ? matches[2].replace('m', '') : '0';
  const seconds = matches[3] ? matches[3].replace('s', '') : '0';
  
  if (hours !== '0') {
    return `${hours}:${minutes.padStart(2, '0')}:${seconds.padStart(2, '0')}`;
  }
  return `${minutes}:${seconds.padStart(2, '0')}`;
};
