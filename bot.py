import os
import logging
import time
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем ключи из переменных окружения
TELEGRAM_BOT_TOKEN = os.environ.get('8218203558:AAHTJEwVnq675p80oEVzVqlsRPqWf9upnP4')
OPENAI_API_KEY = os.environ.get('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')

# Выводим информацию о переменных (для отладки)
print("=" * 50)
print("Проверка переменных окружения:")
print(f"TELEGRAM_BOT_TOKEN: {'УСТАНОВЛЕН' if TELEGRAM_BOT_TOKEN else 'НЕ НАЙДЕН'}")
print(f"OPENAI_API_KEY: {'УСТАНОВЛЕН' if OPENAI_API_KEY else 'НЕ НАЙДЕН'}")
print("=" * 50)

# Проверяем наличие обязательных переменных
if not TELEGRAM_BOT_TOKEN:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: TELEGRAM_BOT_TOKEN не найден!")
    print("Добавьте TELEGRAM_BOT_TOKEN в переменные окружения на Render")
    exit(1)

if not OPENAI_API_KEY:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: OPENAI_API_KEY не найден!")
    print("Добавьте OPENAI_API_KEY в переменные окружения на Render")
    exit(1)

# Инициализируем OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем сообщения от пользователей"""
    
    # Игнорируем сообщения от ботов
    if update.message.from_user.is_bot:
        return
    
    user_message = update.message.text
    user_name = update.message.from_user.first_name
    
    print(f"💬 Получено сообщение от {user_name}: {user_message}")
    
    # Показываем "печатает..."
    await update.message.chat.send_action(action="typing")
    
    try:
        # Получаем ответ от ИИ
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "Ты полезный ассистент в Telegram-группе. Отвечай кратко и понятно. Будь дружелюбным."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        await update.message.reply_text(ai_response)
        print(f"✅ Отправлен ответ пользователю {user_name}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await update.message.reply_text("😔 Произошла ошибка. Попробуйте еще раз.")

def main():
    """Запускаем бота"""
    print("🚀 Запускаем бота...")
    
    # Создаем приложение бота
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчик сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот успешно запущен и готов к работе!")
    print("🤖 Бот работает в режиме 24/7")
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
