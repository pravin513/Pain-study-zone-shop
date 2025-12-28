import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import top_products

ADMIN_ID = int(os.getenv("ADMIN_ID"))

async def admin_menu(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return

    kb = [
        [InlineKeyboardButton("🔥 Top Products", callback_data="a_top")]
    ]

    await update.message.reply_text(
        "⚙️ Admin Panel",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def show_top(update, context):
    rows = top_products()
    msg = "🔥 TOP PRODUCTS\n\n"
    for i,(p,c) in enumerate(rows,1):
        msg += f"{i}. {p} ({c} views)\n"
    await update.message.reply_text(msg)
