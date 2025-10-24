import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем ключи ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

print("Проверка переменных...")
print(f"TELEGRAM_BOT_TOKEN: {'ЕСТЬ' if TELEGRAM_BOT_TOKEN else 'НЕТ'}")
print(f"OPENAI_API_KEY: {'ЕСТЬ' if OPENAI_API_KEY else 'НЕТ'}")

if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    print("ОШИБКА: Не найдены ключи в переменных окружения!")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot:
        return
    
    user_message = update.message.text
    print(f"Сообщение: {user_message}")
    
    await update.message.chat.send_action(action="typing")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты полезный ассистент."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("Ошибка, попробуйте снова.")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
