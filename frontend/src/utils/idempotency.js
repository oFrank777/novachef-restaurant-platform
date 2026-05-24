export function createIdempotencyKey(prefix = 'req') {
  const rand = Math.random().toString(36).slice(2, 12);
  return `${prefix}-${Date.now()}-${rand}`.slice(0, 128);
}
