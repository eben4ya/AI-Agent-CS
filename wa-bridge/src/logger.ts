import pino from 'pino'

export const log = pino({
  level: process.env.LOG_LEVEL || 'info',
  base: undefined,
  timestamp: pino.stdTimeFunctions.isoTime
})

export function safeError(e: unknown): string {
  if (e instanceof Error) return `${e.name}: ${e.message}`
  if (typeof e === 'string') return e
  try { return JSON.stringify(e) } catch { return 'Unknown error' }
}
