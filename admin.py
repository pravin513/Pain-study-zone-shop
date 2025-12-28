import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes
from database import add_product, edit_product, delete_product, top_products

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ======================
# ADMIN CHECK
# ======================
def is_admin(uid):
    return uid == ADMIN_ID

# ======================
# ADMIN DASHBOARD (BUTTON PANEL)
# ======================
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not admin")
        return

    kb = [
        [InlineKeyboardButton("➕ Add Product", callback_data="admin_add")],
        [InlineKeyboardButton("✏️ Edit Product", callback_data="admin_edit")],
        [InlineKeyboardButton("❌ Delete Product", callback_data="admin_delete")],
        [InlineKeyboardButton("📊 Analytics", callback_data="admin_stats")],
        [InlineKeyboardButton("⬅ Exit", callback_data="admin_exit")]
    ]

    await update.message.reply_text(
        "⚙️ ADMIN DASHBOARD\nSelect option 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ======================
# ADMIN BUTTON HANDLER
# ======================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not is_admin(q.from_user.id):
        return

    # ---- ADD PRODUCT ----
    if q.data == "admin_add":
        context.user_data["mode"] = "add"
        await q.message.reply_text(
            "➕ ADD PRODUCT\n\nSend details:\n"
            "Name | category | price | link"
        )
        return

    # ---- EDIT PRODUCT ----
    if q.data == "admin_edit":
        context.user_data["mode"] = "edit"
        await q.message.reply_text(
            "✏️ EDIT PRODUCT\n\nSend:\n"
            "OldName | NewName | category | price | link"
        )
        return

    # ---- DELETE PRODUCT ----
    if q.data == "admin_delete":
        context.user_data["mode"] = "delete"
        await q.message.reply_text(
            "❌ DELETE PRODUCT\n\nSend product name"
        )
        return

    # ---- ANALYTICS ----
    if q.data == "admin_stats":
        rows = top_products()
        msg = "📊 TOP PRODUCTS\n\n"
        if not rows:
            msg += "No data yet"
        else:
            for n, c in rows:
                msg += f"{n} – {c} clicks\n"
        await q.message.reply_text(msg)
        return

    # ---- EXIT ----
    if q.data == "admin_exit":
        context.user_data.clear()
        await q.message.reply_text("✅ Admin panel closed")
        return

# ======================
# ADMIN TEXT INPUT HANDLER
# ======================
async def admin_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    mode = context.user_data.get("mode")
    text = update.message.text.strip()

    # ---- ADD PRODUCT TEXT ----
    if mode == "add":
        parts = text.split("|")
        if len(parts) != 4:
            await update.message.reply_text("❌ Wrong format")
            return

        name, cat, price, link = [x.strip() for x in parts]
        context.user_data["add_data"] = (name, cat, price, link)
        context.user_data["mode"] = "add_photo"

        await update.message.reply_text("📸 Send product photo")
        return

    # ---- EDIT PRODUCT TEXT ----
    if mode == "edit":
        parts = text.split("|")
        if len(parts) != 5:
            await update.message.reply_text("❌ Wrong format")
            return

        old, new, cat, price, link = [x.strip() for x in parts]
        edit_product(old, new, cat, price, link)
        context.user_data.clear()
        await update.message.reply_text("✏️ Product updated")
        return

    # ---- DELETE PRODUCT TEXT ----
    if mode == "delete":
        delete_product(text)
        context.user_data.clear()
        await update.message.reply_text("❌ Product deleted")
        return

# ======================
# ADMIN PHOTO HANDLER
# ======================
async def admin_photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if context.user_data.get("mode") != "add_photo":
        return

    photo_id = update.message.photo[-1].file_id
    name, cat, price, link = context.user_data["add_data"]

    add_product(name, cat, price, link, photo_id)
    context.user_data.clear()

    await update.message.reply_text("✅ Product added successfully")
