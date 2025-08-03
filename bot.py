import asyncio
import aiohttp
import os
import logging
from gtts import gTTS
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TOKEN = os.getenv('BOT_TOKEN')
API_URL = f'https://api.telegram.org/bot{TOKEN}'
offset = 0

async def send_message(chat_id, text):
    async with aiohttp.ClientSession() as session:
        payload = {'chat_id': chat_id, 'text': text}
        await session.post(f'{API_URL}/sendMessage', data=payload)

async def send_photo(chat_id, photo_url):
    async with aiohttp.ClientSession() as session:
        payload = {'chat_id': chat_id, 'photo': photo_url}
        await session.post(f'{API_URL}/sendPhoto', data=payload)

async def send_voice(chat_id, text):
    tts = gTTS(text)
    tts.save("response.ogg")
    async with aiohttp.ClientSession() as session:
        with open("response.ogg", "rb") as f:
            form = aiohttp.FormData()
            form.add_field('chat_id', str(chat_id))
            form.add_field('voice', f, filename='response.ogg', content_type='audio/ogg')
            await session.post(f'{API_URL}/sendVoice', data=form)



async def ask_openai_text(prompt):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    json_data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{"role": "user", "content": prompt}]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("https://api.openai.com/v1/chat/completions",
                                    headers=headers, json=json_data) as resp:
                data = await resp.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content'].strip()
                else:
                    logger.error(f"OpenAI response missing 'choices': {data}")
                    return "❌ OpenAI did not return a valid response."
        except Exception as e:
            logger.exception("Error talking to OpenAI")
            return f"❌ Error talking to OpenAI: {e}"

async def generate_image_from_openai(prompt):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    json_data = {
        "prompt": prompt,
        "n": 1,
        "size": "512x512"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("https://api.openai.com/v1/images/generations",
                                    headers=headers, json=json_data) as resp:
                data = await resp.json()
                if 'data' in data and len(data['data']) > 0:
                    return data['data'][0]['url']
                else:
                    logger.error(f"OpenAI image response error: {data}")
                    return None
        except Exception as e:
            logger.exception("Error generating image from OpenAI")
            return None


async def handle_update(update):
    if 'message' not in update:
        return

    message = update['message']
    chat_id = message['chat']['id']

    # === Text Message ===
    if 'text' in message:
        text = message['text']

        if text.startswith('/start'):
            await send_message(chat_id, "👋 Hello! I'm your async AI-powered bot.")

        elif text.startswith('/help'):
            help_text = (
                "🛠 *Available Commands:*\n\n"
                "/start - Start the bot\n"
                "/ask <question> - Ask OpenAI (text response)\n"
                "/ask image <prompt> - Generate AI image\n"
                "/ask voice <question> - Get voice reply\n"
                "/help - Show this message\n\n"
                "📷 You can also send me *images* or 🎤 *voice messages!*\n"
            )
            await send_message(chat_id, help_text)

        elif text.startswith('/ask image '):
            prompt = text.replace('/ask image ', '', 1).strip()
            if not prompt:
                await send_message(chat_id, "❗ Please provide a prompt for the image.")
            else:
                await send_message(chat_id, "🧠 Generating image...")
                image_url = await generate_image_from_openai(prompt)
                if image_url:
                    await send_photo(chat_id, image_url)
                else:
                    await send_message(chat_id, "❌ Failed to generate image.")

        elif text.startswith('/ask voice '):
            query = text.replace('/ask voice ', '', 1).strip()
            if not query:
                await send_message(chat_id, "❗ Please provide a question.")
            else:
                await send_message(chat_id, "🎤 Thinking and speaking...")
                reply = await ask_openai_text(query)
                await send_voice(chat_id, reply)

        elif text.startswith('/ask '):
            query = text.replace('/ask ', '', 1).strip()
            if not query:
                await send_message(chat_id, "❗ Please provide a question.")
            else:
                await send_message(chat_id, "🧠 Thinking...")
                reply = await ask_openai_text(query)
                await send_message(chat_id, reply)

        else:
            await send_message(chat_id, f"📩 You said: {text}")


    elif 'photo' in message:
        await send_message(chat_id, "📷 Nice image! (received)")


    elif 'voice' in message:
        await send_message(chat_id, "🎤 Voice received! (not transcribed yet)")



async def fetch_updates():
    global offset
    async with aiohttp.ClientSession() as session:
        while True:
            params = {'timeout': 20, 'offset': offset + 1}
            try:
                async with session.get(f'{API_URL}/getUpdates', params=params) as resp:
                    data = await resp.json()
                    for update in data.get('result', []):
                        offset = update['update_id']
                        await handle_update(update)
            except Exception as e:
                logger.exception("Polling error")
                await asyncio.sleep(3)


async def main():
    logger.info("🚀 Bot is running...")
    await fetch_updates()

if __name__ == '__main__':
    asyncio.run(main())
