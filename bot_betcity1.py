import os
import signal
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
from asyncio import to_thread
from parcing1 import match_info

# Загрузка переменных окружения
load_dotenv()

# Получаем токен из переменных окружения
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

if not bot_token:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден. Проверьте .env файл.")

bot = Bot(bot_token)
dp = Dispatcher()
router = Router()

# Глобальный словарь для отслеживания активных пользователей
active_users = set()

# Клавиатура для кнопки "Начать поиск"


def create_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Начать поиск",
                                  callback_data="start_parsing")]])

# Обработчик команды /start


@router.message(Command("start"))
async def start_command(message: types.Message):
    # Отправляем приветственное сообщение только при команде /start
    await message.reply(
        "Привет! Я бот для получения данных о футбольных матчах.\nНажмите кнопку ниже, чтобы начать поиск.",
        reply_markup=create_start_keyboard()
    )


# Обработчик кнопки "Начать поиск"
@router.callback_query(lambda callback: callback.data == "start_parsing")
async def parse_data(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    # Проверяем, запущен ли процесс для пользователя
    if user_id in active_users:
        await callback_query.answer("Подождите, данные уже загружаются!", show_alert=True)
        return

    # Добавляем пользователя в список активных
    active_users.add(user_id)

    try:
        # Уведомляем пользователя о начале загрузки (без приветственного текста)
        await bot.send_message(callback_query.message.chat.id, "Идёт загрузка данных, подождите немного...")

        # Вызываем функцию парсинга данных
        info = await to_thread(match_info)

        if not info:
            await bot.send_message(callback_query.message.chat.id, "Матчи с нужными данными не найдены.")

        else:
            for match in info:
                match_list = [value for key, value in match.items()]
                info_to_tg = (
                    f"Матч: {match_list[0]};\n"
                    f"Счёт в матче: {match_list[2]};\n"
                    f"Красные карточки: {
                        match_list[1][0]} - {match_list[1][1]};\n"
                    f"Угловые: {match_list[4][0]} - {match_list[4][1]};\n"
                    f"Удары по воротам: {
                        match_list[5][0]} - {match_list[5][1]};\n"
                    f"Удары в створ: {match_list[6]
                                      [0]} - {match_list[6][1]};\n"
                    f"Время матча: {match_list[3]}.\n"
                    f"Коэффициенты на победу: {match_list[7]
                                               [0]} - {match_list[7][1]};\n"
                )
                await bot.send_message(callback_query.message.chat.id, info_to_tg)
            print(info_to_tg)

        # Предлагаем начать новый поиск
        await bot.send_message(
            callback_query.message.chat.id,
            "Поиск завершён. Нажмите на кнопку ниже, чтобы начать новый поиск.",
            reply_markup=create_start_keyboard()
        )

    except Exception as e:
        print(f"Ошибка: {e}")
        await callback_query.message.reply("Ошибка при загрузке данных. Попробуйте ещё раз.")
    finally:
        # Удаляем пользователя из активных после завершения
        active_users.remove(user_id)

# Обработчик завершения программы


def signal_handler(sig, frame):
    print("Программа завершена.")
    asyncio.get_event_loop().stop()


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    import asyncio

    async def main():
        dp.include_router(router)
        await dp.start_polling(bot)

    asyncio.run(main())
