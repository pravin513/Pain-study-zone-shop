import sqlite3

def connect():
    return sqlite3.connect("data.db")

def init_db():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price TEXT,
        link TEXT,
        photo TEXT,
        clicks INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS cart(
        user_id INTEGER,
        name TEXT,
        price TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS favorites(
        user_id INTEGER,
        name TEXT,
        price TEXT,
        link TEXT,
        photo TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS referrals(
        user_id INTEGER UNIQUE,
        count INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

# ---------- PRODUCTS ----------
def add_product(name, category, price, link, photo):
    conn = connect()
    conn.execute(
        "INSERT INTO products(name,category,price,link,photo) VALUES (?,?,?,?,?)",
        (name, category, price, link, photo)
    )
    conn.commit()
    conn.close()

def edit_product(old_name, name, category, price, link):
    conn = connect()
    conn.execute(
        "UPDATE products SET name=?,category=?,price=?,link=? WHERE name=?",
        (name, category, price, link, old_name)
    )
    conn.commit()
    conn.close()

def delete_product(name):
    conn = connect()
    conn.execute("DELETE FROM products WHERE name=?", (name,))
    conn.commit()
    conn.close()

def get_by_category(cat, limit, offset):
    conn = connect()
    rows = conn.execute(
        "SELECT name,price,link,photo FROM products WHERE category=? LIMIT ? OFFSET ?",
        (cat, limit, offset)
    ).fetchall()
    conn.close()
    return rows

def track_click(name):
    conn = connect()
    conn.execute(
        "UPDATE products SET clicks=clicks+1 WHERE name=?",
        (name,)
    )
    conn.commit()
    conn.close()

def top_products(limit=5):
    conn = connect()
    rows = conn.execute(
        "SELECT name,clicks FROM products ORDER BY clicks DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows

# ---------- CART ----------
def add_cart(uid, name, price):
    conn = connect()
    conn.execute(
        "INSERT INTO cart(user_id,name,price) VALUES (?,?,?)",
        (uid, name, price)
    )
    conn.commit()
    conn.close()

def get_cart(uid):
    conn = connect()
    rows = conn.execute(
        "SELECT name,price FROM cart WHERE user_id=?",
        (uid,)
    ).fetchall()
    conn.close()
    return rows

# ---------- FAVORITES ----------
def add_fav(uid, name, price, link, photo):
    conn = connect()
    conn.execute(
        "INSERT INTO favorites(user_id,name,price,link,photo) VALUES (?,?,?,?,?)",
        (uid, name, price, link, photo)
    )
    conn.commit()
    conn.close()

def get_fav(uid):
    conn = connect()
    rows = conn.execute(
        "SELECT name,price,link,photo FROM favorites WHERE user_id=?",
        (uid,)
    ).fetchall()
    conn.close()
    return rows

# ---------- REFERRAL ----------
def get_referral(uid):
    conn = connect()
    row = conn.execute(
        "SELECT count FROM referrals WHERE user_id=?",
        (uid,)
    ).fetchone()
    conn.close()
    return row[0] if row else 0

def add_referral(uid):
    conn = connect()
    row = conn.execute(
        "SELECT count FROM referrals WHERE user_id=?",
        (uid,)
    ).fetchone()

    if row:
        conn.execute(
            "UPDATE referrals SET count=count+1 WHERE user_id=?",
            (uid,)
        )
    else:
        conn.execute(
            "INSERT INTO referrals(user_id,count) VALUES (?,1)",
            (uid,)
        )
    conn.commit()
    conn.close()

def referral_leaderboard(limit=5):
    conn = connect()
    rows = conn.execute(
        "SELECT user_id,count FROM referrals ORDER BY count DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows
