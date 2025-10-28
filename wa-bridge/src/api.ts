import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { env } from './env'
import type { IncomingMessagePayload, AgentReplyRequest, AgentReplyResponse, WebhookResponse } from './types'

/**
 * ApiClient: wrapper untuk call backend FastAPI.
 * - POST /webhook/whatsapp
 * - POST /agent/reply
 */
export class ApiClient {
  private http: AxiosInstance

  constructor(baseURL = env.API_BASE) {
    this.http = axios.create({ baseURL, timeout: 15000 })
  }

  async postWebhook(payload: IncomingMessagePayload): Promise<WebhookResponse> {
    const { data } = await this.http.post<WebhookResponse>('/webhook/whatsapp', payload)
    return data
  }

  async postAgentReply(body: AgentReplyRequest): Promise<AgentReplyResponse> {
    const { data } = await this.http.post<AgentReplyResponse>('/agent/reply', body)
    return data
  }
}
