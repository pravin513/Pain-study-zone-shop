import os
from telegram import *
from telegram.ext import *
from database import *
from admin import *

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")

# ---------- START ----------
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
        "Welcome 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ---------- BUTTONS ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data == "cart":
        items = get_cart(uid)
        if not items:
            await q.message.reply_text("Cart empty")
            return
        msg = "Cart:\n"
        for n,p in items:
            msg += f"{n} – ₹{p}\n"
        await q.message.reply_text(msg)
        return

    cat,page = q.data.split(":")
    page = int(page)
    rows = get_by_category(cat,5,page*5)

    for n,p,l,ph in rows:
        track_click(n)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Cart", callback_data=f"add|{n}|{p}")],
            [InlineKeyboardButton("❤️ Save", callback_data=f"fav|{n}|{p}|{l}|{ph}")],
            [InlineKeyboardButton("🛒 Buy", url=l)]
        ])
        await q.message.reply_photo(ph,f"{n}\n₹{p}",reply_markup=kb)

# ---------- CART ----------
async def cart_add(update, context):
    q = update.callback_query
    _,n,p = q.data.split("|")
    add_cart(q.from_user.id,n,p)
    await q.message.reply_text("Added to cart")

# ---------- SAVE ----------
async def fav_add(update, context):
    q = update.callback_query
    _,n,p,l,ph = q.data.split("|")
    add_fav(q.from_user.id,n,p,l,ph)
    await q.message.reply_text("Saved ❤️")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CommandHandler("addproduct", addproduct))
    app.add_handler(CommandHandler("editproduct", editproduct))
    app.add_handler(CommandHandler("deleteproduct", deleteproduct))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("leaderboard", leaderboard))

    app.add_handler(CallbackQueryHandler(cart_add, pattern="^add"))
    app.add_handler(CallbackQueryHandler(fav_add, pattern="^fav"))
    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, addproduct_details))
    app.add_handler(MessageHandler(filters.PHOTO, addproduct_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, editproduct_details))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, deleteproduct_name))

    app.run_polling()

if __name__ == "__main__":
    main()
