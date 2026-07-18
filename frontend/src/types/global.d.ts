declare global {
  interface Window {
    $message?: {
      success: (content: string) => void
      error: (content: string) => void
      warning: (content: string) => void
      info: (content: string) => void
    }
    PlotPilotFeedback?: {
      /** 控制台：触发与 UI 同构的事故快照 */
      reportError: (summary: string, err?: unknown) => void
      peekRecentIncidents: () => Array<{
        summary: string
        occurred_at: string
        detail_length: number
      }>
      exportRecentBundle: () => void
      /** 清除后端不可用时的历史错误（502/503/504/网络错误） */
      clearBackendUnavailableIncidents: () => void
    }
  }
}

export {}
