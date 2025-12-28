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
    MessageHandler,
    ContextTypes,
    filters
)

from database import *
from admin import (
    admin_menu,
    admin_buttons,
    admin_text_input,
    admin_photo_input
)

# =======================
# ENV
# =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")

# =======================
# START (USER)
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_db()
    context.application.bot_data.setdefault("users", set()).add(update.effective_user.id)

    kb = [
        [InlineKeyboardButton("👗 Saree", callback_data="saree:0")],
        [InlineKeyboardButton("📱 Gadgets", callback_data="gadgets:0")],
        [InlineKeyboardButton("🎁 Gift", callback_data="gift:0")],
        [InlineKeyboardButton("🛒 Cart", callback_data="cart")]
    ]

    await update.message.reply_text(
        "👋 Welcome to Pravin Study Zone Shop\nChoose category 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# =======================
# USER BUTTONS
# =======================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # -------- CART --------
    if q.data == "cart":
        items = get_cart(uid)
        if not items:
            await q.message.reply_text("🛒 Cart empty")
            return

        msg = "🛒 Your Cart\n"
        for n, p in items:
            msg += f"\n• {n} – ₹{p}"
        await q.message.reply_text(msg)
        return

    # -------- CATEGORY --------
    try:
        cat, page = q.data.split(":")
        page = int(page)
    except:
        return

    rows = get_by_category(cat, 5, page * 5)
    if not rows:
        await q.message.reply_text("❌ No products")
        return

    for n, p, l, ph in rows:
        track_click(n)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Cart", callback_data=f"add|{n}|{p}")],
            [InlineKeyboardButton("❤️ Save", callback_data=f"fav|{n}|{p}|{l}|{ph}")],
            [InlineKeyboardButton("🛒 Buy", url=l)]
        ])
        await q.message.reply_photo(
            photo=ph,
            caption=f"{n}\n💰 ₹{p}",
            reply_markup=kb
        )

# =======================
# CART ADD
# =======================
async def cart_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, n, p = q.data.split("|")
    add_cart(q.from_user.id, n, p)
    await q.message.reply_text("✅ Added to cart")

# =======================
# SAVE (FAVORITE)
# =======================
async def fav_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, n, p, l, ph = q.data.split("|")
    add_fav(q.from_user.id, n, p, l, ph)
    await q.message.reply_text("❤️ Saved")

# =======================
# MAIN
# =======================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ---- USER ----
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cart_add, pattern="^add"))
    app.add_handler(CallbackQueryHandler(fav_add, pattern="^fav"))
    app.add_handler(CallbackQueryHandler(buttons))

    # ---- ADMIN (PRO PANEL) ----
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CallbackQueryHandler(admin_buttons, pattern="^admin_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_text_input))
    app.add_handler(MessageHandler(filters.PHOTO, admin_photo_input))

    print("🚀 PROFESSIONAL BOT STARTED")
    app.run_polling()

if __name__ == "__main__":
    main()
