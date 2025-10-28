import 'dotenv/config'
import { Client, LocalAuth, Message } from 'whatsapp-web.js'
import qrcode from 'qrcode-terminal'
import { ApiClient } from './api'
import { log, safeError } from './logger'

async function main() {
  const api = new ApiClient()

  const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { args: ['--no-sandbox', '--disable-setuid-sandbox'] }
  })

  client.on('qr', (qr: string) => {
    qrcode.generate(qr, { small: true })
    log.info('🔐 Scan QR untuk login WhatsApp...')
  })

  client.on('ready', () => {
    log.info('✅ WhatsApp client siap')
  })

  client.on('message', async (msg: Message) => {
    const from = msg.from
    const text = msg.body ?? ''

    try {
      await api.postWebhook({ from, text })
      log.info({ from }, 'Webhook logged')
    } catch (e) {
      log.error({ err: safeError(e) }, 'Webhook gagal')
    }

    try {
      const res = await api.postAgentReply({ from, text })
      if (res.reply) {
        await client.sendMessage(from, res.reply)
        log.info({ from }, 'Reply sent')
      } else {
        log.warn({ from }, 'No reply from agent')
      }
    } catch (e) {
      log.error({ err: safeError(e) }, 'Agent reply gagal')
    }
  })

  await client.initialize()
}

main().catch((err) => {
  log.fatal({ err: safeError(err) }, 'Fatal error')
  process.exit(1)
})
