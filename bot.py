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
logger = logging.getLogger(__name__)

# Получаем ключи из переменных окружения
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

print("=" * 50)
print("Проверка переменных окружения:")
print(f"TELEGRAM_BOT_TOKEN: {'✅ УСТАНОВЛЕН' if TELEGRAM_BOT_TOKEN else '❌ НЕ НАЙДЕН'}")
print(f"OPENAI_API_KEY: {'✅ УСТАНОВЛЕН' if OPENAI_API_KEY else '❌ НЕ НАЙДЕН'}")
print("=" * 50)

# Проверяем наличие обязательных переменных
if not TELEGRAM_BOT_TOKEN:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: TELEGRAM_BOT_TOKEN не найден!")
    exit(1)

if not OPENAI_API_KEY:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: OPENAI_API_KEY не найден!")
    exit(1)

# Инициализируем OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем ответы на бота и упоминания через @"""
    
    if update.message.from_user.is_bot:
        return
    
    user_message = update.message.text
    user_name = update.message.from_user.first_name
    bot_username = (await context.bot.get_me()).username
    
    # Проверяем, является ли сообщение ответом на сообщение бота
    is_reply_to_bot = (
        update.message.reply_to_message and 
        update.message.reply_to_message.from_user and
        update.message.reply_to_message.from_user.username == bot_username
    )
    
    # Проверяем, есть ли упоминание бота через @
    is_direct_mention = f"@{bot_username}" in user_message
    is_command = user_message.startswith('/')
    
    # Отвечаем только если: ответ на бота ИЛИ прямое упоминание ИЛИ команда
    should_respond = is_reply_to_bot or is_direct_mention or is_command
    
    if not should_respond:
        print(f"❌ Игнорируем сообщение от {user_name} (не ответ боту и не упоминание)")
        return
    
    print(f"💬 Обрабатываем сообщение от {user_name}: {user_message}")
    
    # Очищаем сообщение от упоминания
    clean_message = user_message.replace(f"@{bot_username}", "").strip()
    
    # Если это команда (кроме /start), убираем команду
    if clean_message.startswith('/') and not clean_message.startswith('/start'):
        clean_message = ' '.join(clean_message.split(' ')[1:])
    
    await update.message.chat.send_action(action="typing")
    
    try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",  # Самая свежая версия GPT-3.5
        messages=[
            {
                "role": "system", 
                "content": "Ты полезный ассистент в Telegram-группе. Отвечай кратко и понятно на русском. Текущий год: 2024."
            },
            {
                "role": "user", 
                "content": clean_message
            }
        ],
        max_tokens=500
    )
        
        ai_response = response.choices[0].message.content
        
        # ВСЕГДА отвечаем reply на исходное сообщение пользователя
        await update.message.reply_text(ai_response, reply_to_message_id=update.message.message_id)
        print(f"✅ Ответ отправлен пользователю {user_name} (reply)")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await update.message.reply_text("😔 Произошла ошибка. Попробуйте еще раз.", reply_to_message_id=update.message.message_id)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - показывает справку"""
    bot_username = (await context.bot.get_me()).username
    help_text = (
        "🤖 *Помощь по боту:*\n\n"
        "*Способы обращения:*\n"
        "• Ответьте (reply) на любое мое сообщение\n"
        "• Упоминание @{} в любом месте сообщения\n"
        "• Команда /ask [вопрос]\n\n"
        "*Примеры:*\n"
        "`@{} Как дела?`\n"
        "`/ask Напиши код`\n"
        "Или просто ответьте на это сообщение!"
    ).format(bot_username, bot_username)
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def post_init(application: Application):
    """Функция, которая выполняется после инициализации бота"""
    print("✅ Бот инициализирован!")

async def post_stop(application: Application):
    """Функция, которая выполняется при остановке бота"""
    print("🛑 Бот остановлен")

def main():
    """Запускаем бота"""
    print("🚀 Запускаем бота...")
    
    try:
        # Создаем приложение бота с обработчиками событий
        application = (
            Application.builder()
            .token(TELEGRAM_BOT_TOKEN)
            .post_init(post_init)
            .post_stop(post_stop)
            .build()
        )
        
        # Добавляем обработчик сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот успешно запущен и готов к работе!")
        print("🤖 Бот работает в режиме 24/7")
        print("📱 Добавьте бота в группу и напишите сообщение для теста")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске бота: {e}")
        exit(1)

if __name__ == '__main__':
    main()
