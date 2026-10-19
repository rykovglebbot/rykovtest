import asyncio
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# Вставь НОВЫЙ токен бота от @BotFather.
# Не публикуй токен и не отправляй его посторонним.
TOKEN = "ВСТАВЬ_НОВЫЙ_ТОКЕН_ОТ_BOTFATHER"

# Username администратора без символа @
ADMIN_USERNAME = "crystal671488"

# URL твоего Telegram Mini App — замени YOUR-USERNAME на свой GitHub username
WEB_APP_URL = "https://YOUR-USERNAME.github.io/rykov-kombat/"

# Файл для сохранения пользователей
USERS_FILE = "users.txt"

bot = Bot(token=TOKEN)
dp = Dispatcher()


def add_user(chat_id: int) -> None:
    """Добавляет ID пользователя в файл, не создавая дубликатов."""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            users = set(file.read().splitlines())
    except FileNotFoundError:
        users = set()

    users.add(str(chat_id))

    with open(USERS_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(sorted(users)))


def get_all_users() -> list[int]:
    """Возвращает список ID пользователей из файла."""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return [int(uid) for uid in file.read().splitlines() if uid.strip()]
    except FileNotFoundError:
        return []


def is_admin(message: types.Message) -> bool:
    """Проверяет username отправителя."""
    username = message.from_user.username if message.from_user else None
    return bool(username and username.casefold() == ADMIN_USERNAME.casefold())


@dp.message(Command("start"))
async def start_cmd(message: types.Message) -> None:
    add_user(message.chat.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💪 Играть в Rykov Kombat",
                    web_app=WebAppInfo(url=WEB_APP_URL),
                )
            ]
        ]
    )

    await message.answer(
        "Добро пожаловать в *Rykov Kombat*!\n"
        "Тапай по экрану, прокачивай бицепсы и зарабатывай коины!",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@dp.message(Command("mes"))
async def broadcast_cmd(message: types.Message) -> None:
    if not is_admin(message):
        await message.answer("❌ У вас нет прав на эту функцию.")
        return

    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.answer(
            "⚠️ Напиши текст после команды, например:\n"
            "`/mes Обновление игры! Заходите тапать!`",
            parse_mode="Markdown",
        )
        return

    text_to_broadcast = args[1]
    users = get_all_users()
    success_count = 0

    for chat_id in users:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"📢 Сообщение от создателя:\n\n{text_to_broadcast}",
            )
            success_count += 1
        except Exception as exc:
            logging.warning("Не удалось отправить сообщение пользователю %s: %s", chat_id, exc)

    await message.answer(
        f"✅ Рассылка завершена! Сообщение доставлено пользователям: {success_count}"
    )


@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message) -> None:
    if not is_admin(message):
        await message.answer("❌ У вас нет прав на эту функцию.")
        return

    text_from_web = message.web_app_data.data
    users = get_all_users()
    success_count = 0

    for chat_id in users:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"📢 Сообщение от создателя:\n\n{text_from_web}",
            )
            success_count += 1
        except Exception as exc:
            logging.warning("Не удалось отправить сообщение пользователю %s: %s", chat_id, exc)

    await message.answer(
        f"✅ Рассылка из игры завершена! Получили: {success_count} пользователей."
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    if TOKEN == "ВСТАВЬ_НОВЫЙ_ТОКЕН_ОТ_BOTFATHER":
        raise RuntimeError(
            "Сначала вставь новый токен бота в переменную TOKEN."
        )

    if "YOUR-USERNAME" in WEB_APP_URL:
        raise RuntimeError(
            "Сначала замени YOUR-USERNAME в WEB_APP_URL на свой GitHub username."
        )

    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
