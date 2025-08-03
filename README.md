# Async Telegram Bot with OpenAI

This project is an asynchronous Telegram bot powered by OpenAI's GPT API. Built using `aiohttp`, it supports text replies, voice responses, and AI-generated images. All responses are handled in real-time using polling and asyncio.

---

## Features

* Text-based chat using GPT-3.5-turbo
* Voice reply using gTTS (text-to-speech)
* AI-generated image responses via DALL·E
* Asynchronous architecture with `aiohttp` and `asyncio`
* Command support: `/ask`, `/ask voice`, `/ask image`, `/help`

---

## Requirements

* Python 3.8+
* Telegram Bot Token from [@BotFather](https://t.me/BotFather)
* OpenAI API Key from [https://platform.openai.com](https://platform.openai.com)

---

## Setup

1. Install dependencies:

   ```bash
   pip install aiohttp python-dotenv gTTS
   ```

2. Create a `.env` file:

   ```
   BOT_TOKEN=your_telegram_token
   OPENAI_API_KEY=your_openai_key
   ```

3. Run the bot:

   ```bash
   python bot.py
   ```

---

## Commands

* `/start` — Welcome message
* `/help` — List available commands
* `/ask <text>` — Ask a question, get a text reply
* `/ask voice <text>` — Ask a question, get a voice reply
* `/ask image <prompt>` — Generate an image from a prompt

---

## License

MIT License
