import 'dotenv/config'
import { Client, LocalAuth, Message } from 'whatsapp-web.js'
import qrcode from 'qrcode-terminal'
import { ApiClient } from './api'

async function main() {
  const api = new ApiClient()

  const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { args: ['--no-sandbox', '--disable-setuid-sandbox'] }
  })

  client.on('qr', (qr: string) => {
    qrcode.generate(qr, { small: true })
    console.log('🔐 Scan QR untuk login WhatsApp...')
  })

  client.on('ready', () => {
    console.log('✅ WhatsApp client siap')
  })

  client.on('message', async (msg: Message) => {
    const from = msg.from
    const text = msg.body ?? ''

    // 1) Kirim pesan masuk ke webhook (logging)
    try {
      await api.postWebhook({ from, text })
    } catch (e) {
      console.error('⚠️ Gagal kirim webhook:', e)
    }

    // 2) Minta balasan dari Agent
    try {
      const res = await api.postAgentReply({ from, text })
      if (res.reply) {
        await client.sendMessage(from, res.reply)
      }
    } catch (e) {
      console.error('⚠️ Gagal minta balasan Agent:', e)
    }
  })

  await client.initialize()
}

main().catch((err) => {
  console.error('❌ Fatal error:', err)
  process.exit(1)
})
