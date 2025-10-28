# WA Bridge (TypeScript)

## Dev
```

npm i
cp .env.example .env
npm run dev

```
- Scan QR di terminal (login WhatsApp).
- Pastikan `API_BASE` mengarah ke FastAPI (default: `http://localhost:8000`).

## Production
```

npm run build
npm start

```

## Troubleshooting
- **QR tidak muncul**: pastikan terminal cukup lebar; coba hapus folder `.wwebjs_auth`.
- **Tidak balas**: cek FastAPI hidup, endpoint `/agent/reply` valid, dan `API_BASE` benar.
- **Sandbox Chromium**: sudah set `--no-sandbox`, cocok untuk Docker/CI.
