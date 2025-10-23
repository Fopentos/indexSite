import os
import json
import random
import datetime
from collections import defaultdict
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# 🔧 НАСТРОЙКИ БОТА
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Токен из настроек Heroku

# 💰 ПАКЕТЫ ПОПОЛНЕНИЯ
PRODUCTS = {
    "pack_5": {"title": "5 Игровых звезд ⭐", "description": "Пополнение баланса на 5 игровых звезд", "price": 5, "credits": 5},
    "pack_10": {"title": "10 Игровых звезд ⭐⭐", "description": "Пополнение баланса на 10 игровых звезд", "price": 10, "credits": 10},
    "pack_25": {"title": "25 Игровых звезд 💫", "description": "Пополнение баланса на 25 игровых звезд", "price": 25, "credits": 25},
    "pack_50": {"title": "50 Игровых звезд 💎", "description": "Пополнение баланса на 50 игровых звезд", "price": 50, "credits": 50},
    "pack_100": {"title": "100 Игровых звезд 🔥", "description": "Пополнение баланса на 100 игровых звезд", "price": 100, "credits": 100},
    "pack_250": {"title": "250 Игровых звезд 🏆", "description": "Пополнение баланса на 250 игровых звезд", "price": 250, "credits": 250},
    "pack_500": {"title": "500 Игровых звезд 🚀", "description": "Пополнение баланса на 500 игровых звезд", "price": 500, "credits": 500},
    "pack_1000": {"title": "1000 Игровых звезд 💰", "description": "Пополнение баланса на 1000 игровых звезд", "price": 1000, "credits": 1000}
}

# 🎰 НАСТРОЙКИ ИГР
GAMES = ["🎰", "🎯", "🎲", "🎳", "⚽", "🏀"]

# 🗃️ БАЗА ДАННЫХ
user_data = defaultdict(lambda: {'balance': 100, 'games_played': 0, 'wins': 0, 'total_deposited': 0})

# 💾 СОХРАНЕНИЕ ДАННЫХ
def save_data():
    try:
        with open('data.json', 'w') as f:
            json.dump(dict(user_data), f)
    except: pass

def load_data():
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            user_data.update(data)
    except: pass

# 🤖 ИНИЦИАЛИЗАЦИЯ БОТА
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# 🏠 КОМАНДА /start
@router.message(Command("start"))
async def start_cmd(message: Message):
    text = """
🎰 <b>ZETA CASINO BOT</b> 🎰
Добро пожаловать в казино!
💫 <b>Игры:</b>
🎰 Слоты - 5⭐ 🎯 Дартс - 5⭐ 🎲 Кубик - 5⭐
🎳 Боулинг - 5⭐ ⚽ Футбол - 5⭐ 🏀 Баскетбол - 5⭐
💰 <b>Пополнение:</b> 1 Telegram Star = 1 игровая звезда
/profile - Твой профиль | /deposit - Пополнить баланс
    """
    await message.answer(text, parse_mode=ParseMode.HTML)

# 👤 КОМАНДА /profile  
@router.message(Command("profile"))
async def profile_cmd(message: Message):
    user_id = message.from_user.id
    data = user_data[user_id]
    text = f"👤 <b>ЛИЧНЫЙ КАБИНЕТ</b>\n\n💰 Баланс: {data['balance']} ⭐\n🎮 Игр: {data['games_played']}\n🏆 Побед: {data['wins']}\n💎 Пополнено: {data['total_deposited']} ⭐"
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="💳 Пополнить", callback_data="deposit")
    keyboard.button(text="🎮 Играть", callback_data="play_menu")
    keyboard.adjust(2)
    await message.answer(text, reply_markup=keyboard.as_markup(), parse_mode=ParseMode.HTML)

# 💳 ПОПОЛНЕНИЕ БАЛАНСА
@router.message(Command("deposit"))
async def deposit_cmd(message: Message):
    keyboard = InlineKeyboardBuilder()
    for key, product in PRODUCTS.items():
        keyboard.button(text=f"{product['title']} - {product['price']}⭐", callback_data=f"buy_{key}")
    keyboard.button(text="🔙 Назад", callback_data="back_profile")
    keyboard.adjust(1)
    await message.answer("💳 <b>ВЫБЕРИ ПАКЕТ ПОПОЛНЕНИЯ</b>\n\n1 Telegram Star = 1 игровая звезда", reply_markup=keyboard.as_markup(), parse_mode=ParseMode.HTML)

# 🎮 МЕНЮ ИГР
@router.callback_query(F.data == "play_menu")
async def play_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    balance = user_data[user_id]['balance']
    keyboard = InlineKeyboardBuilder()
    for game in GAMES:
        keyboard.button(text=f"{game} Играть (5⭐)", callback_data=f"play_{game}")
    keyboard.button(text="💳 Пополнить", callback_data="deposit")
    keyboard.button(text="👤 Профиль", callback_data="back_profile")
    keyboard.adjust(2)
    await callback.message.edit_text(f"🎮 <b>ВЫБЕРИ ИГРУ</b>\n\n💰 Баланс: {balance}⭐", reply_markup=keyboard.as_markup(), parse_mode=ParseMode.HTML)
    await callback.answer()

# 🎯 ОБРАБОТКА ИГР
@router.callback_query(F.data.startswith("play_"))
async def play_game(callback: CallbackQuery):
    user_id = callback.from_user.id
    game_emoji = callback.data.replace("play_", "")
    if user_data[user_id]['balance'] < 5:
        await callback.answer("❌ Недостаточно средств! Пополни баланс.", show_alert=True)
        return
    user_data[user_id]['balance'] -= 5
    user_data[user_id]['games_played'] += 1
    await callback.message.answer_dice(emoji=game_emoji)
    await callback.message.edit_text(f"🎮 Игра {game_emoji} запущена!\n💰 Списано: 5⭐\n💫 Осталось: {user_data[user_id]['balance']}⭐")
    save_data()
    await callback.answer()

# 🎰 ОБРАБОТКА РЕЗУЛЬТАТОВ ИГР
@router.message(F.dice)
async def handle_dice_result(message: Message):
    user_id = message.from_user.id
    dice = message.dice
    if dice.emoji == "🎰":
        if dice.value in [1, 22, 43, 64]:
            win_amount = {1: 50, 22: 25, 43: 15, 64: 100}[dice.value]
            user_data[user_id]['balance'] += win_amount
            user_data[user_id]['wins'] += 1
            await message.answer(f"🎉 <b>ДЖЕКПОТ!</b>\n💫 Выигрыш: {win_amount}⭐\n💰 Баланс: {user_data[user_id]['balance']}⭐", parse_mode=ParseMode.HTML)
        else:
            await message.answer(f"😢 Не повезло...\n💰 Баланс: {user_data[user_id]['balance']}⭐")
    else:
        if dice.value == 6:
            user_data[user_id]['balance'] += 15
            user_data[user_id]['wins'] += 1
            await message.answer(f"🎉 <b>ПОБЕДА!</b> +15⭐\n💰 Баланс: {user_data[user_id]['balance']}⭐", parse_mode=ParseMode.HTML)
        else:
            await message.answer(f"😢 Мимо...\n💰 Баланс: {user_data[user_id]['balance']}⭐")
    save_data()

# 💰 ОПЛАТА TELEGRAM STARS
@router.callback_query(F.data.startswith("buy_"))
async def handle_payment(callback: CallbackQuery):
    product_key = callback.data.replace("buy_", "")
    product = PRODUCTS[product_key]
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Оплатить {product['price']}⭐", pay=True)
    await callback.message.answer_invoice(
        title=product["title"],
        description=product["description"],
        payload=product_key,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=product["title"], amount=product["price"])],
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

# ✅ ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА
@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

# 💎 УСПЕШНЫЙ ПЛАТЕЖ
@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    user_id = message.from_user.id
    product_key = payment.invoice_payload
    product = PRODUCTS[product_key]
    user_data[user_id]['balance'] += product["credits"]
    user_data[user_id]['total_deposited'] += product["credits"]
    save_data()
    await message.answer(f"💎 <b>ПЛАТЕЖ ПРОШЕЛ!</b>\n\n✅ Зачислено: {product['credits']} игровых звезд\n💰 Баланс: {user_data[user_id]['balance']}⭐", parse_mode=ParseMode.HTML)

# 🔙 ОБРАБОТКА КНОПОК НАЗАД
@router.callback_query(F.data == "back_profile")
async def back_to_profile(callback: CallbackQuery):
    await profile_cmd(callback.message)
    await callback.answer()

@router.callback_query(F.data == "deposit")
async def deposit_callback(callback: CallbackQuery):
    await deposit_cmd(callback.message)
    await callback.answer()

# 📞 КОМАНДА PAYSUPPORT
@router.message(Command("paysupport"))
async def pay_support(message: Message):
    await message.answer("📞 <b>ПОДДЕРЖКА ПО ПЛАТЕЖАМ</b>\n\nВозврат средств возможен в течение 14 дней.\nДля возврата напишите в поддержку.", parse_mode=ParseMode.HTML)

# 🚀 ЗАПУСК БОТА
async def main():
    load_data()
    print("🎰 Zeta Casino Bot ЗАПУЩЕН на Heroku!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())