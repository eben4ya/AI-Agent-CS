# AI Agent Customer Service

## Project Overview

We’re building a WhatsApp-ready customer-service copilot that keeps pace with busy chat traffic. Incoming messages arrive through a `whatsapp-web.js` bridge, flow into our FastAPI backend, and then hit a LangChain-powered agent that calls Gemini 2.5 Flash for reasoning. The agent can pull product, store, and shipping data straight from Supabase-backed APIs, remembers the ongoing conversation, and writes every turn back to `chat_logs` for auditing.

## Architecture

![AI Agent Architecture](./AI-Agent-CS%20Architecture.png)

## How to Run

1. Clone the repo and move into it:
   ```bash
   git clone git@github.com:eben4ya/AI-Agent-CS.git
   cd AI-Agent-CS
   ```
2. Create the backend virtualenv (Python 3.12) and install dependencies:
   ```bash
   cd backend/app
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` in `backend/app/`, then fill in your Supabase DSN, RajaOngkir key, and Gemini credentials.
4. Apply database migrations in `backend/app/db`.
5. Launch the FastAPI service:
   ```bash
   uvicorn app.main:app --port 8000 --reload
   ```
6. In a second terminal, install and run the WhatsApp bridge:
   ```bash
   cd wa-bridge
   npm install
   npm run build
   npm run start
   ```
   Scan the QR code with your WhatsApp account to pair the bot.
7. The AI customer-service assistant now responds to WhatsApp messages in real time.

## Full Report

Dive into the full Notion write-up—prompt design, testing, limitations, and future work included:  
[AI Agent Customer Service Report →](https://jolly-bee-29a.notion.site/AI-Agent-Customer-Service-29c050bafece80119c83f8344629599d?source=copy_link)

## Demo

https://github.com/user-attachments/assets/b2958508-8440-43a6-9315-75ba0cd02e60
