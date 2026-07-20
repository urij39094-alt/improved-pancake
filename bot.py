import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# -------------------- НАСТРОЙКИ --------------------
BOT_TOKEN = "8305139904:AAFYTIWtK0y21R7UwGozH5k226QDm6gGl9g"
OPENROUTER_TOKEN = "AQ.Ab8RN6IOsa7ELLqzCzyuW9wl2g9m5wu4Re2A0dRJE9W3kOAfzQ"
MODEL = "google/gemini-2.0-flash-001"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# ----------------------------------------------------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Ты ImpulseAI — дружелюбный и полезный ассистент в Telegram. Отвечай коротко и по делу."
}
user_context = {}

# -------------------- ФУНКЦИЯ ЗАПРОСА К OPENROUTER --------------------
async def ask_ai(messages: list) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_TOKEN}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/ImpulseAibot",
        "X-Title": "ImpulseAibot"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(OPENROUTER_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"OpenRouter error {resp.status}: {error_text}")
            data = await resp.json()
            return data["choices"][0]["message"]["content"]

# -------------------- ОБРАБОТЧИКИ --------------------
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(
        f"👋 Привет, {msg.from_user.first_name}!\n\n"
        f"Я ImpulseAI — бот с мозгами от Gemini.\n"
        f"Просто напиши мне что-нибудь, и я отвечу.\n\n"
        f"Команды:\n"
        f"/clear — очистить историю диалога\n"
        f"/start — это сообщение"
    )

@dp.message(Command("clear"))
async def clear_cmd(msg: types.Message):
    user_id = msg.from_user.id
    if user_id in user_context:
        del user_context[user_id]
    await msg.answer("✅ История диалога очищена.")

@dp.message()
async def ai_chat(msg: types.Message):
    user_id = msg.from_user.id
    
    if user_id not in user_context:
        user_context[user_id] = [SYSTEM_PROMPT]
    
    user_context[user_id].append({"role": "user", "content": msg.text})
    
    await bot.send_chat_action(msg.chat.id, "typing")
    
    try:
        answer = await ask_ai(user_context[user_id])
        user_context[user_id].append({"role": "assistant", "content": answer})
        await msg.answer(answer)
        
    except Exception as e:
        logging.error(f"AI error: {e}")
        await msg.answer("⚠️ Сорян, технические неполадки. Попробуй позже.")

# -------------------- ЗАПУСК --------------------
async def main():
    logging.basicConfig(level=logging.INFO)
    print("ImpulseAibot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())