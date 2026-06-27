import telebot
from telebot import types

BOT_TOKEN = "8739053922:AAE8a4LEi1k-hF1EakGoVaXE7ZjQQctzX94"
ADMIN_CHAT_ID = "8094888670"

bot = telebot.TeleBot(BOT_TOKEN)

MENU = {
    "🍔 Бургеры": [
        {"name": "Биг чиккен Б", "price": 40000},
        {"name": "Биг бургер", "price": 42000},
        {"name": "Чиккен чиз", "price": 30000},
        {"name": "Чизбургер", "price": 35000},
        {"name": "Гамбургер", "price": 32000},
    ],
    "🌯 Донары": [
        {"name": "Донар блюдо", "price": 60000},
        {"name": "Искандар", "price": 65000},
        {"name": "Донар", "price": 38000},
        {"name": "Донар с сыром", "price": 40000},
        {"name": "Донар средний", "price": 35000},
    ],
    "🥙 Хаггиси": [
        {"name": "Куринный хагги", "price": 35000},
        {"name": "Мясной хагги", "price": 42000},
        {"name": "Грибной хагги", "price": 42000},
    ],
    "🫓 Лаваш": [
        {"name": "Лаваш с мясом", "price": 42000},
        {"name": "Лаваш с сыром", "price": 42000},
        {"name": "Лаваш с куринный", "price": 35000},
        {"name": "Тандир лаваш", "price": 50000},
    ],
    "🌭 Хот-доги": [
        {"name": "Хот дог стандарт", "price": 20000},
        {"name": "Биг Хот дог", "price": 24000},
        {"name": "Королевский", "price": 26000},
    ],
    "🍕 Пицца": [
        {"name": "Куринный средний", "price": 80000},
        {"name": "Куринный большой", "price": 100000},
        {"name": "Пепперони средний", "price": 75000},
        {"name": "Пепперони большой", "price": 90000},
        {"name": "Комбо средний", "price": 105000},
        {"name": "Комбо большой", "price": 120000},
        {"name": "Мясной средний", "price": 105000},
        {"name": "Мясной большой", "price": 120000},
        {"name": "Донар средний", "price": 105000},
        {"name": "Донар большой", "price": 120000},
        {"name": "Грибной средний", "price": 70000},
        {"name": "Грибной большой", "price": 80000},
    ],
    "🍟 Закуски": [
        {"name": "Фри деревянкий", "price": 20000},
        {"name": "Фри", "price": 20000},
        {"name": "Клаб сандвия мясной", "price": 47000},
        {"name": "Клаб сандвия куринный", "price": 42000},
    ],
}

carts = {}

def get_cart(uid): return carts.setdefault(uid, [])
def fmt(n): return f"{n:,}".replace(",", " ") + " сум"
def cart_total(uid): return sum(i["price"]*i["qty"] for i in get_cart(uid))
def cart_summary(uid):
    cart = get_cart(uid)
    if not cart: return "Корзина пуста."
    lines = [f"• {i['name']} x{i['qty']} — {fmt(i['price']*i['qty'])}" for i in cart]
    lines.append(f"\n💰 Итого: {fmt(cart_total(uid))}")
    return "\n".join(lines)

def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 Меню", "🛒 Корзина")
    kb.row("✅ Оформить заказ", "❌ Очистить корзину")
    return kb

def cats_kb():
    kb = types.InlineKeyboardMarkup()
    for cat in MENU: kb.add(types.InlineKeyboardButton(cat, callback_data=f"cat:{cat}"))
    return kb

def items_kb(cat):
    kb = types.InlineKeyboardMarkup()
    for item in MENU[cat]:
        kb.add(types.InlineKeyboardButton(f"{item['name']} — {fmt(item['price'])}", callback_data=f"add:{cat}:{item['name']}"))
    kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back"))
    return kb

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "👋 Добро пожаловать в *RETRO BURGER*! 🍔\n\nВыберите действие:", parse_mode="Markdown", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == "📋 Меню")
def menu(m): bot.send_message(m.chat.id, "Выберите категорию:", reply_markup=cats_kb())

@bot.message_handler(func=lambda m: m.text == "🛒 Корзина")
def cart(m): bot.send_message(m.chat.id, f"🛒 *Корзина:*\n\n{cart_summary(m.from_user.id)}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "❌ Очистить корзину")
def clear(m):
    carts[m.from_user.id] = []
    bot.send_message(m.chat.id, "✅ Корзина очищена.")

@bot.message_handler(func=lambda m: m.text == "✅ Оформить заказ")
def checkout(m):
    if not get_cart(m.from_user.id):
        bot.send_message(m.chat.id, "🛒 Корзина пуста!")
        return
    bot.send_message(m.chat.id, "📞 Введите ваш номер телефона:")
    bot.register_next_step_handler(m, get_phone)

def get_phone(m):
    u = m.from_user
    try:
        bot.send_message(ADMIN_CHAT_ID, f"🔔 *Новый заказ!*\n👤 {u.first_name} (@{u.username or 'нет'})\n📞 {m.text}\n\n{cart_summary(u.id)}", parse_mode="Markdown")
    except: pass
    bot.send_message(m.chat.id, f"✅ *Заказ принят!*\nПозвоним на {m.text} 🍔", parse_mode="Markdown", reply_markup=main_kb())
    carts[u.id] = []

@bot.callback_query_handler(func=lambda c: c.data == "back")
def cb_back(c): bot.edit_message_text("Выберите категорию:", c.message.chat.id, c.message.message_id, reply_markup=cats_kb())

@bot.callback_query_handler(func=lambda c: c.data.startswith("cat:"))
def cb_cat(c): bot.edit_message_text(c.data[4:], c.message.chat.id, c.message.message_id, reply_markup=items_kb(c.data[4:]))

@bot.callback_query_handler(func=lambda c: c.data.startswith("add:"))
def cb_add(c):
    _, cat, name = c.data.split(":", 2)
    item = next((i for i in MENU[cat] if i["name"] == name), None)
    if not item: return
    cart = get_cart(c.from_user.id)
    ex = next((i for i in cart if i["name"] == name), None)
    if ex: ex["qty"] += 1
    else: cart.append({**item, "qty": 1})
    bot.answer_callback_query(c.id, f"✅ {name} добавлен!")
    bot.send_message(c.message.chat.id, f"➕ *{name}* добавлен!\n\n{cart_summary(c.from_user.id)}", parse_mode="Markdown")

print("🍔 RETRO BURGER запущен!")
bot.infinity_polling()
