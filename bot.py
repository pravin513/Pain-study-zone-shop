import os
from telegram import *
from telegram.ext import *
from database import *
from smart_search import normalize
from admin import admin_menu, show_top

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_step("start")
    kb = [
        [InlineKeyboardButton("🔥 Today Best Deals", callback_data="today:0")],
        [InlineKeyboardButton("👗 Saree", callback_data="saree:0"),
         InlineKeyboardButton("📱 Gadgets", callback_data="gadgets:0")],
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

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "cart":
        items = get_cart(q.from_user.id)
        if not items:
            await q.message.reply_text("🛒 Cart खाली है")
            return
        msg = "🛒 Your Cart\n"
        for n,p in items:
            msg += f"\n• {n} – {p}"
        await q.message.reply_text(msg)
        return

    if q.data == "saved":
        rows = get_fav(q.from_user.id)
        if not rows:
            await q.message.reply_text("❌ कुछ भी save नहीं है")
            return
        for n,p,l,ph in rows:
            await q.message.reply_photo(
                ph, f"{n}\n💰 {p}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🛒 Buy", url=l)]]
                )
            )
        return

    if q.data == "refer":
        uid = q.from_user.id
        link = f"https://t.me/{context.bot.username}?start=REF{uid}"
        count = get_referral(uid)
        await q.message.reply_text(
            f"🧲 Share & Earn\n\n{link}\n\n👥 Referrals: {count}"
        )
        return

    if q.data == "help":
        await q.message.reply_text(
            "ℹ️ इस्तेमाल कैसे करें:\n"
            "1️⃣ Category चुनें\n"
            "2️⃣ Product देखें\n"
            "3️⃣ Save / Cart करें\n"
            "4️⃣ Buy button दबाएँ"
        )
        return

    if q.data == "a_top":
        await show_top(q.message, context)
        return

    cat, page = q.data.split(":")
    page = int(page)
    rows = get_by_category(cat, 5, page*5)

    for n,p,l,ph in rows:
        track_click(n)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Cart", callback_data=f"add|{n}|{p}")],
            [InlineKeyboardButton("❤️ Save", callback_data=f"fav|{n}")],
            [InlineKeyboardButton("🛒 Buy", url=l)]
        ])
        await q.message.reply_photo(ph, f"{n}\n💰 {p}", reply_markup=kb)

async def cart_add(update, context):
    q = update.callback_query
    _,n,p = q.data.split("|")
    add_cart(q.from_user.id, n, p)
    track_step("cart_add")
    await q.message.reply_text("✅ Cart में जोड़ दिया")

async def fav_add(update, context):
    q = update.callback_query
    name = q.data.split("|")[1]
    await q.message.reply_text("❤️ Saved")

def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CallbackQueryHandler(cart_add, pattern="add"))
    app.add_handler(CallbackQueryHandler(fav_add, pattern="fav"))
    app.add_handler(CallbackQueryHandler(buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
