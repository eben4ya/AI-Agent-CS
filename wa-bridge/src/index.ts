import 'dotenv/config'
import { Client, LocalAuth } from 'whatsapp-web.js'
import qrcode from 'qrcode-terminal'

/**
 * Bootstrap WhatsApp client (TypeScript).
 * - Tampilkan QR di terminal
 * - Log ketika client siap
 */
async function main() {
  const client = new Client({
    authStrategy: new LocalAuth(), // simpan session lokal .wwebjs_auth
    puppeteer: {
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
  })

  client.on('qr', (qr: string) => {
    qrcode.generate(qr, { small: true })
    console.log('🔐 Scan QR untuk login WhatsApp...')
  })

  client.on('ready', () => {
    console.log('✅ WhatsApp client siap')
  })

  await client.initialize()
}

main().catch((err) => {
  console.error('❌ Fatal error:', err)
  process.exit(1)
})
