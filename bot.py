import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from database import *
from admin import admin_menu, show_top

# =======================
# ENV
# =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN missing in environment")

# =======================
# START
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_db()

    kb = [
        [InlineKeyboardButton("🔥 Today Best Deals", callback_data="today:0")],
        [
            InlineKeyboardButton("👗 Saree", callback_data="saree:0"),
            InlineKeyboardButton("📱 Gadgets", callback_data="gadgets:0")
        ],
        [InlineKeyboardButton("🎁 Gift Ideas", callback_data="gift:0")],
        [InlineKeyboardButton("🛒 My Cart", callback_data="cart")],
        [InlineKeyboardButton("❤️ Saved", callback_data="saved")],
        [InlineKeyboardButton("🧲 Share & Earn", callback_data="refer")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]

    await update.message.reply_text(
        "🙏 स्वागत है\nनीचे से चुनिए 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# =======================
# BUTTON HANDLER
# =======================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    # CART
    if q.data == "cart":
        items = get_cart(uid)
        if not items:
            await q.message.reply_text("🛒 Cart खाली है")
            return

        msg = "🛒 Your Cart\n"
        for n, p in items:
            msg += f"\n• {n} – {p}"
        await q.message.reply_text(msg)
        return

    # SAVED
    if q.data == "saved":
        rows = get_fav(uid)
        if not rows:
            await q.message.reply_text("❌ कुछ भी save नहीं है")
            return

        for n, p, l, ph in rows:
            await q.message.reply_photo(
                photo=ph,
                caption=f"{n}\n💰 {p}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🛒 Buy", url=l)]]
                )
            )
        return

    # REFER
    if q.data == "refer":
        link = f"https://t.me/{context.bot.username}?start=REF{uid}"
        count = get_referral(uid)
        await q.message.reply_text(
            f"🧲 Share & Earn\n\n{link}\n\n👥 Referrals: {count}"
        )
        return

    # HELP
    if q.data == "help":
        await q.message.reply_text(
            "ℹ️ इस्तेमाल कैसे करें:\n"
            "1️⃣ Category चुनें\n"
            "2️⃣ Product देखें\n"
            "3️⃣ Save / Cart करें\n"
            "4️⃣ Buy button दबाएँ"
        )
        return

    # ADMIN TOP
    if q.data == "a_top":
        await show_top(q.message, context)
        return

    # CATEGORY PAGINATION
    cat, page = q.data.split(":")
    page = int(page)

    rows = get_by_category(cat, limit=5, offset=page * 5)

    if not rows:
        await q.message.reply_text("❌ कोई product नहीं मिला")
        return

    for n, p, l, ph in rows:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Cart", callback_data=f"add|{n}|{p}")],
            [InlineKeyboardButton("❤️ Save", callback_data=f"fav|{n}")],
            [InlineKeyboardButton("🛒 Buy", url=l)]
        ])
        await q.message.reply_photo(
            photo=ph,
            caption=f"{n}\n💰 {p}",
            reply_markup=kb
        )

# =======================
# CART ADD
# =======================
async def cart_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, n, p = q.data.split("|")
    add_cart(q.from_user.id, n, p)
    await q.message.reply_text("✅ Cart में जोड़ दिया")

# =======================
# FAVORITE
# =======================
async def fav_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    name = q.data.split("|")[1]
    add_fav(q.from_user.id, name)
    await q.message.reply_text("❤️ Saved")

# =======================
# MAIN
# =======================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_menu))

    app.add_handler(CallbackQueryHandler(cart_add, pattern="^add"))
    app.add_handler(CallbackQueryHandler(fav_add, pattern="^fav"))
    app.add_handler(CallbackQueryHandler(buttons))

    print("✅ Bot started successfully")
    app.run_polling()

if __name__ == "__main__":
    main()
