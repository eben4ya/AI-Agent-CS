export interface IncomingMessagePayload {
    from: string
    text: string
  }
  
  export interface AgentReplyRequest {
    from: string
    text: string
  }
  
  export interface AgentReplyResponse {
    reply?: string
  }
  
  export interface WebhookResponse {
    ok: boolean
  }
  