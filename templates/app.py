from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"  # для сессий (корзины)

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return render_template("index.html", products=products)

# --- КОРЗИНА ---
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    return redirect(url_for("index"))

@app.route("/cart")
def cart():
    if "cart" not in session or len(session["cart"]) == 0:
        return render_template("cart.html", cart=[], total=0)

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    products = []
    total = 0
    for pid in session["cart"]:
        cur.execute("SELECT * FROM products WHERE id=?", (pid,))
        item = cur.fetchone()
        if item:
            products.append(item)
            total += item[2]
    conn.close()
    return render_template("cart.html", cart=products, total=total)

# --- АДМИНКА ---
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()
        return redirect(url_for("admin"))

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return render_template("admin.html", products=products)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
