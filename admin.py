import os
from telegram import Update
from telegram.ext import ContextTypes
from database import *

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

def is_admin(uid):
    return uid == ADMIN_ID

# ---------- ADMIN PANEL ----------
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not admin")
        return

    await update.message.reply_text(
        "⚙️ ADMIN PANEL\n\n"
        "/addproduct\n"
        "/editproduct\n"
        "/deleteproduct\n"
        "/stats\n"
        "/leaderboard"
    )

# ---------- ADD PRODUCT ----------
async def addproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    context.user_data["add"] = True
    await update.message.reply_text(
        "Send:\nName | category | price | link"
    )

async def addproduct_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("add"):
        return
    data = update.message.text.split("|")
    if len(data) != 4:
        await update.message.reply_text("❌ Wrong format")
        return
    context.user_data["pdata"] = [x.strip() for x in data]
    context.user_data["add"] = "photo"
    await update.message.reply_text("📸 Send product photo")

async def addproduct_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("add") != "photo":
        return
    photo = update.message.photo[-1].file_id
    name, cat, price, link = context.user_data["pdata"]
    add_product(name, cat, price, link, photo)
    context.user_data.clear()
    await update.message.reply_text("✅ Product added")

# ---------- EDIT PRODUCT ----------
async def editproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    context.user_data["edit"] = True
    await update.message.reply_text(
        "Send:\nOldName | NewName | category | price | link"
    )

async def editproduct_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("edit"):
        return
    data = update.message.text.split("|")
    if len(data) != 5:
        await update.message.reply_text("❌ Wrong format")
        return
    old,n,c,p,l = [x.strip() for x in data]
    edit_product(old,n,c,p,l)
    context.user_data.clear()
    await update.message.reply_text("🔁 Product updated")

# ---------- DELETE PRODUCT ----------
async def deleteproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    context.user_data["del"] = True
    await update.message.reply_text("Send product name to delete")

async def deleteproduct_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("del"):
        return
    delete_product(update.message.text.strip())
    context.user_data.clear()
    await update.message.reply_text("🗑️ Product deleted")

# ---------- STATS ----------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    rows = top_products()
    msg = "📊 TOP PRODUCTS\n\n"
    for n,c in rows:
        msg += f"{n} – {c} clicks\n"
    await update.message.reply_text(msg)

# ---------- LEADERBOARD ----------
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    rows = referral_leaderboard()
    msg = "🧲 REFERRAL LEADERBOARD\n\n"
    for uid,c in rows:
        msg += f"{uid} → {c}\n"
    await update.message.reply_text(msg)
