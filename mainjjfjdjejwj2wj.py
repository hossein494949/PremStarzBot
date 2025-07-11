from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "7683436515:AAHFAqhqA9eIu7ItNGTatMwn3Tmzgq40kic"
ADMIN_ID = 6754963226

user_balances = {}
prices = {"premium": 50000, "starz": 30000}

main_menu = ReplyKeyboardMarkup([
    [KeyboardButton("🎁 ثبت سفارش جدید")],
    [KeyboardButton("💰 موجودی"), KeyboardButton("📞 پشتیبانی")],
    [KeyboardButton("📢 کانال ما")]
], resize_keyboard=True)

order_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🟡 پریمیوم", callback_data="order_premium")],
    [InlineKeyboardButton("🌟 استارز", callback_data="order_starz")],
    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
])

admin_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("📊 مشاهده سفارش‌ها", callback_data="admin_orders")],
    [InlineKeyboardButton("💲 تغییر قیمت‌ها", callback_data="admin_prices")],
    [InlineKeyboardButton("➕ افزایش موجودی", callback_data="admin_balance")]
])

orders = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in user_balances:
        user_balances[user.id] = 0
    await update.message.reply_text("سلام به PremStarz خوش اومدی! ✨", reply_markup=main_menu)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "🎁 ثبت سفارش جدید":
        await update.message.reply_text("سرویس مورد نظر رو انتخاب کن:", reply_markup=order_menu)
    elif text == "📞 پشتیبانی":
        await update.message.reply_text("پشتیبانی : @TeknoSup")
    elif text == "📢 کانال ما":
        await update.message.reply_text("https://t.me/PremStarzReport")
    elif text == "💰 موجودی":
        bal = user_balances.get(user.id, 0)
        await update.message.reply_text(f"موجودی شما: {bal} تومان")
    elif user.id == ADMIN_ID and text == "/admin":
        await update.message.reply_text("پنل مدیریت:", reply_markup=admin_menu)
    else:
        await update.message.reply_text("دستور نامشخصه. از منو استفاده کن.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data == "order_premium":
        cost = prices["premium"]
        if user_balances.get(user.id, 0) >= cost:
            user_balances[user.id] -= cost
            orders.append(f"🟡 سفارش پریمیوم از {user.full_name} (@{user.username})")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 سفارش پریمیوم از {user.full_name} (@{user.username})")
            await query.edit_message_text("✅ سفارش ثبت شد.")
        else:
            await query.edit_message_text("❌ موجودی شما کافی نیست.")
    elif query.data == "order_starz":
        cost = prices["starz"]
        if user_balances.get(user.id, 0) >= cost:
            user_balances[user.id] -= cost
            orders.append(f"🌟 سفارش استارز از {user.full_name} (@{user.username})")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 سفارش استارز از {user.full_name} (@{user.username})")
            await query.edit_message_text("✅ سفارش ثبت شد.")
        else:
            await query.edit_message_text("❌ موجودی شما کافی نیست.")
    elif query.data == "back_to_main":
        await query.edit_message_text("بازگشت به منو")
    elif user.id == ADMIN_ID:
        if query.data == "admin_orders":
            await query.edit_message_text("\n".join(orders[-10:]) or "هیچ سفارشی ثبت نشده.")
        elif query.data == "admin_prices":
            await query.edit_message_text("برای تغییر قیمت از دستور استفاده کن:

/setprice premium 60000")
        elif query.data == "admin_balance":
            await query.edit_message_text("برای افزایش موجودی:

/addbal USER_ID AMOUNT")

async def set_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) == 2 and args[0] in prices:
        prices[args[0]] = int(args[1])
        await update.message.reply_text(f"قیمت {args[0]} تنظیم شد روی {args[1]} تومان")
    else:
        await update.message.reply_text("فرمت: /setprice نوع مبلغ")

async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) == 2:
        uid = int(args[0])
        amt = int(args[1])
        user_balances[uid] = user_balances.get(uid, 0) + amt
        await update.message.reply_text(f"{amt} تومان به کاربر {uid} اضافه شد.")
    else:
        await update.message.reply_text("فرمت: /addbal USER_ID AMOUNT")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setprice", set_price))
    app.add_handler(CommandHandler("addbal", add_balance))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()