import sqlite3

def connect():
    return sqlite3.connect("data.db")

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        keywords TEXT,
        price TEXT,
        link TEXT,
        photo TEXT,
        priority INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart(
        user_id INTEGER,
        product TEXT,
        price TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites(
        user_id INTEGER,
        name TEXT,
        price TEXT,
        link TEXT,
        photo TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS referrals(
        user_id INTEGER PRIMARY KEY,
        count INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics(
        product TEXT,
        clicks INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS journey(
        step TEXT,
        count INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

# ---------- PRODUCTS ----------
def add_product(name, category, keywords, price, link, photo):
    conn = connect()
    conn.execute(
        "INSERT INTO products(name,category,keywords,price,link,photo) VALUES (?,?,?,?,?,?)",
        (name, category, keywords, price, link, photo)
    )
    conn.commit()
    conn.close()

def get_by_category(cat, limit=5, offset=0):
    conn = connect()
    rows = conn.execute(
        "SELECT name,price,link,photo FROM products WHERE category=? ORDER BY priority DESC LIMIT ? OFFSET ?",
        (cat, limit, offset)
    ).fetchall()
    conn.close()
    return rows

def search_products(text):
    conn = connect()
    rows = conn.execute(
        "SELECT name,price,link,photo,category FROM products WHERE keywords LIKE ?",
        (f"%{text}%",)
    ).fetchall()
    conn.close()
    return rows

# ---------- CART ----------
def add_cart(uid, product, price):
    conn = connect()
    conn.execute(
        "INSERT INTO cart(user_id,product,price) VALUES (?,?,?)",
        (uid, product, price)
    )
    conn.commit()
    conn.close()

def get_cart(uid):
    conn = connect()
    rows = conn.execute(
        "SELECT product,price FROM cart WHERE user_id=?",
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

# ---------- ANALYTICS ----------
def track_click(product):
    conn = connect()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT clicks FROM analytics WHERE product=?",
        (product,)
    ).fetchone()

    if row:
        cur.execute(
            "UPDATE analytics SET clicks=clicks+1 WHERE product=?",
            (product,)
        )
    else:
        cur.execute(
            "INSERT INTO analytics(product,clicks) VALUES (?,1)",
            (product,)
        )

    conn.commit()
    conn.close()

def top_products(limit=5):
    conn = connect()
    rows = conn.execute(
        "SELECT product,clicks FROM analytics ORDER BY clicks DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows

# ---------- USER JOURNEY ----------
def track_step(step):
    conn = connect()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT count FROM journey WHERE step=?",
        (step,)
    ).fetchone()

    if row:
        cur.execute(
            "UPDATE journey SET count=count+1 WHERE step=?",
            (step,)
        )
    else:
        cur.execute(
            "INSERT INTO journey(step,count) VALUES (?,1)",
            (step,)
        )

    conn.commit()
    conn.close()
