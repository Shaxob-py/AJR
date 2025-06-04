import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import json
import sqlite3
from datetime import datetime
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - replace with your actual bot token
BOT_TOKEN = "7499424910:AAGpgYAkoxeDe_bMh26s3tEIHiyx5kCeY1M"


class PharmaBotDB:
    def __init__(self):
        self.conn = sqlite3.connect('pharma_bot.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Users table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id
                           INTEGER
                           PRIMARY
                           KEY,
                           username
                           TEXT,
                           first_name
                           TEXT,
                           phone
                           TEXT,
                           address
                           TEXT,
                           registration_date
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Products table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS products
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           NOT
                           NULL,
                           description
                           TEXT,
                           price
                           REAL
                           NOT
                           NULL,
                           stock
                           INTEGER
                           DEFAULT
                           0,
                           category
                           TEXT,
                           image_url
                           TEXT,
                           requires_prescription
                           BOOLEAN
                           DEFAULT
                           0
                       )
                       ''')

        # Orders table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS orders
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER,
                           products
                           TEXT,
                           total_amount
                           REAL,
                           status
                           TEXT
                           DEFAULT
                           'pending',
                           order_date
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           delivery_address
                           TEXT,
                           phone
                           TEXT
                       )
                       ''')

        # Cart table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS cart
                       (
                           user_id
                           INTEGER,
                           product_id
                           INTEGER,
                           quantity
                           INTEGER,
                           PRIMARY
                           KEY
                       (
                           user_id,
                           product_id
                       )
                           )
                       ''')

        self.conn.commit()
        self.populate_sample_products()

    def populate_sample_products(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ("Paracetamol 500mg", "Pain relief and fever reducer", 5.99, 100, "Pain Relief", None, 0),
                ("Ibuprofen 400mg", "Anti-inflammatory pain relief", 8.50, 75, "Pain Relief", None, 0),
                ("Vitamin C 1000mg", "Immune system support", 12.99, 50, "Vitamins", None, 0),
                ("Amoxicillin 500mg", "Antibiotic for bacterial infections", 15.99, 30, "Antibiotics", None, 1),
                ("Blood Pressure Monitor", "Digital BP monitoring device", 45.99, 20, "Medical Devices", None, 0),
                ("Thermometer Digital", "Accurate temperature measurement", 19.99, 40, "Medical Devices", None, 0),
            ]

            cursor.executemany('''
                               INSERT INTO products (name, description, price, stock, category, image_url,
                                                     requires_prescription)
                               VALUES (?, ?, ?, ?, ?, ?, ?)
                               ''', sample_products)
            self.conn.commit()


# Initialize database
db = PharmaBotDB()


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Register user
    cursor = db.conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    ''', (user.id, user.username, user.first_name))
    db.conn.commit()

    welcome_text = f"""
🏥 **Welcome to PharmaBot!** 🏥

Hello {user.first_name}! 

I'm your pharmaceutical assistant. Here's what I can help you with:

💊 Browse medications and health products
🛒 Add items to your cart
📋 Place orders
📍 Track your orders
💳 Secure payment processing

⚠️ **Important Notice:**
- Some medications require a valid prescription
- Please consult healthcare professionals before use
- We comply with all pharmaceutical regulations

Use the menu below to get started!
    """

    keyboard = [
        [KeyboardButton("🛍️ Browse Products"), KeyboardButton("🛒 My Cart")],
        [KeyboardButton("📋 My Orders"), KeyboardButton("📞 Contact Support")],
        [KeyboardButton("ℹ️ About Us"), KeyboardButton("⚙️ Settings")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')


# Browse products
async def browse_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = db.conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = cursor.fetchall()

    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(f"📦 {category[0]}", callback_data=f"category_{category[0]}")])

    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🛍️ **Product Categories**\n\nSelect a category to browse products:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


# Show products by category
async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    products = cursor.fetchall()

    if not products:
        await update.callback_query.answer("No products found in this category.")
        return

    text = f"📦 **{category}**\n\n"
    keyboard = []

    for product in products:
        id_, name, desc, price, stock, cat, img, prescription = product
        status = "✅ In Stock" if stock > 0 else "❌ Out of Stock"
        prescription_text = " 🔒 Rx Required" if prescription else ""

        text += f"**{name}**{prescription_text}\n"
        text += f"💰 ${price:.2f} | {status}\n"
        text += f"📝 {desc}\n\n"

        if stock > 0:
            keyboard.append([InlineKeyboardButton(f"🛒 Add {name}", callback_data=f"add_to_cart_{id_}")])

    keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="browse_products")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


# Add to cart
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    user_id = update.effective_user.id

    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        await update.callback_query.answer("Product not found.")
        return

    if product[4] <= 0:  # stock
        await update.callback_query.answer("Product out of stock.")
        return

    # Add to cart
    cursor.execute('''
        INSERT OR REPLACE INTO cart (user_id, product_id, quantity)
        VALUES (?, ?, COALESCE((SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?), 0) + 1)
    ''', (user_id, product_id, user_id, product_id))
    db.conn.commit()

    await update.callback_query.answer(f"✅ {product[1]} added to cart!")


# Show cart
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor = db.conn.cursor()
    cursor.execute('''
                   SELECT p.name, p.price, c.quantity, p.id
                   FROM cart c
                            JOIN products p ON c.product_id = p.id
                   WHERE c.user_id = ?
                   ''', (user_id,))

    cart_items = cursor.fetchall()

    if not cart_items:
        await update.message.reply_text("🛒 Your cart is empty!")
        return

    text = "🛒 **Your Cart**\n\n"
    total = 0
    keyboard = []

    for item in cart_items:
        name, price, quantity, product_id = item
        item_total = price * quantity
        total += item_total

        text += f"**{name}**\n"
        text += f"💰 ${price:.2f} x {quantity} = ${item_total:.2f}\n\n"

        keyboard.append([
            InlineKeyboardButton(f"➖", callback_data=f"decrease_{product_id}"),
            InlineKeyboardButton(f"{quantity}", callback_data=f"quantity_{product_id}"),
            InlineKeyboardButton(f"➕", callback_data=f"increase_{product_id}"),
            InlineKeyboardButton(f"🗑️", callback_data=f"remove_{product_id}")
        ])

    text += f"**Total: ${total:.2f}**"

    keyboard.append([InlineKeyboardButton("🛍️ Checkout", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🔙 Continue Shopping", callback_data="browse_products")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# Checkout process
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Get cart items
    cursor = db.conn.cursor()
    cursor.execute('''
                   SELECT p.name, p.price, c.quantity, p.requires_prescription
                   FROM cart c
                            JOIN products p ON c.product_id = p.id
                   WHERE c.user_id = ?
                   ''', (user_id,))

    cart_items = cursor.fetchall()

    if not cart_items:
        await update.callback_query.answer("Your cart is empty!")
        return

    # Check for prescription requirements
    prescription_required = any(item[3] for item in cart_items)

    text = "🛍️ **Checkout Summary**\n\n"
    total = 0

    for item in cart_items:
        name, price, quantity, prescription = item
        item_total = price * quantity
        total += item_total
        prescription_text = " 🔒" if prescription else ""
        text += f"{name}{prescription_text} x{quantity} - ${item_total:.2f}\n"

    text += f"\n**Total: ${total:.2f}**\n\n"

    if prescription_required:
        text += "⚠️ **Prescription Required**\n"
        text += "Some items in your cart require a valid prescription. You'll need to upload your prescription during the order process.\n\n"

    text += "📍 Please provide your delivery address and phone number to complete the order."

    keyboard = [
        [InlineKeyboardButton("📝 Provide Details", callback_data="provide_details")],
        [InlineKeyboardButton("🔙 Back to Cart", callback_data="show_cart")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


# Handle button callbacks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "browse_products":
        await browse_products(update, context)
    elif query.data.startswith("category_"):
        category = query.data.replace("category_", "")
        await show_category_products(update, context, category)
    elif query.data.startswith("add_to_cart_"):
        product_id = int(query.data.replace("add_to_cart_", ""))
        await add_to_cart(update, context, product_id)
    elif query.data == "checkout":
        await checkout(update, context)
    elif query.data == "provide_details":
        await query.edit_message_text(
            "📝 **Order Details**\n\n"
            "Please send me your delivery information in this format:\n\n"
            "**Address:** Your full delivery address\n"
            "**Phone:** Your contact number\n\n"
            "Example:\n"
            "Address: 123 Main St, City, State 12345\n"
            "Phone: +1-555-0123"
        )


# Handle text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛍️ Browse Products":
        await browse_products(update, context)
    elif text == "🛒 My Cart":
        await show_cart(update, context)
    elif text == "📋 My Orders":
        await show_orders(update, context)
    elif text == "📞 Contact Support":
        await update.message.reply_text(
            "📞 **Contact Support**\n\n"
            "For assistance, please contact us:\n"
            "📧 Email: support@pharmabot.com\n"
            "📱 Phone: +1-800-PHARMA\n"
            "🕒 Hours: 9 AM - 6 PM (Mon-Fri)\n\n"
            "We're here to help with your pharmaceutical needs!"
        )
    elif text == "ℹ️ About Us":
        await update.message.reply_text(
            "ℹ️ **About PharmaBot**\n\n"
            "We are a licensed pharmaceutical retailer committed to providing:\n\n"
            "✅ Genuine medications\n"
            "✅ Professional consultation\n"
            "✅ Fast, secure delivery\n"
            "✅ Regulatory compliance\n\n"
            "**License:** [Your License Number]\n"
            "**Established:** 2024\n\n"
            "Your health is our priority! 🏥"
        )


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor = db.conn.cursor()
    cursor.execute('''
                   SELECT id, products, total_amount, status, order_date
                   FROM orders
                   WHERE user_id = ?
                   ORDER BY order_date DESC LIMIT 10
                   ''', (user_id,))

    orders = cursor.fetchall()

    if not orders:
        await update.message.reply_text("📋 You have no orders yet.")
        return

    text = "📋 **Your Recent Orders**\n\n"

    for order in orders:
        order_id, products, total, status, date = order
        status_emoji = {"pending": "⏳", "confirmed": "✅", "shipped": "🚚", "delivered": "📦"}.get(status, "❓")

        text += f"**Order #{order_id}**\n"
        text += f"{status_emoji} Status: {status.title()}\n"
        text += f"💰 Total: ${total:.2f}\n"
        text += f"📅 Date: {date[:10]}\n\n"

    await update.message.reply_text(text, parse_mode='Markdown')


def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("🤖 PharmaBot is starting...")
    application.run_polling()


if __name__ == '__main__':
    main()
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import json
import sqlite3
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - replace with your actual bot token
BOT_TOKEN = "7499424910:AAGpgYAkoxeDe_bMh26s3tEIHiyx5kCeY1M"

class PharmaBotDB:
    def __init__(self):
        self.conn = sqlite3.connect('pharma_bot.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                phone TEXT,
                address TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                category TEXT,
                image_url TEXT,
                requires_prescription BOOLEAN DEFAULT 0
            )
        ''')

        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                products TEXT,
                total_amount REAL,
                status TEXT DEFAULT 'pending',
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivery_address TEXT,
                phone TEXT
            )
        ''')

        # Cart table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                PRIMARY KEY (user_id, product_id)
            )
        ''')

        self.conn.commit()
        self.populate_sample_products()

    def populate_sample_products(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ("Paracetamol 500mg", "Pain relief and fever reducer", 5.99, 100, "Pain Relief", None, 0),
                ("Ibuprofen 400mg", "Anti-inflammatory pain relief", 8.50, 75, "Pain Relief", None, 0),
                ("Vitamin C 1000mg", "Immune system support", 12.99, 50, "Vitamins", None, 0),
                ("Amoxicillin 500mg", "Antibiotic for bacterial infections", 15.99, 30, "Antibiotics", None, 1),
                ("Blood Pressure Monitor", "Digital BP monitoring device", 45.99, 20, "Medical Devices", None, 0),
                ("Thermometer Digital", "Accurate temperature measurement", 19.99, 40, "Medical Devices", None, 0),
            ]

            cursor.executemany('''
                INSERT INTO products (name, description, price, stock, category, image_url, requires_prescription)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_products)
            self.conn.commit()

# Initialize database
db = PharmaBotDB()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Register user
    cursor = db.conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    ''', (user.id, user.username, user.first_name))
    db.conn.commit()

    welcome_text = f"""
🏥 **Welcome to PharmaBot!** 🏥

Hello {user.first_name}! 

I'm your pharmaceutical assistant. Here's what I can help you with:

💊 Browse medications and health products
🛒 Add items to your cart
📋 Place orders
📍 Track your orders
💳 Secure payment processing

⚠️ **Important Notice:**
- Some medications require a valid prescription
- Please consult healthcare professionals before use
- We comply with all pharmaceutical regulations

Use the menu below to get started!
    """

    keyboard = [
        [KeyboardButton("🛍️ Browse Products"), KeyboardButton("🛒 My Cart")],
        [KeyboardButton("📋 My Orders"), KeyboardButton("📞 Contact Support")],
        [KeyboardButton("ℹ️ About Us"), KeyboardButton("⚙️ Settings")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# Browse products
async def browse_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = db.conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = cursor.fetchall()

    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(f"📦 {category[0]}", callback_data=f"category_{category[0]}")])

    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🛍️ **Product Categories**\n\nSelect a category to browse products:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Show products by category
async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    products = cursor.fetchall()

    if not products:
        await update.callback_query.answer("No products found in this category.")
        return

    text = f"📦 **{category}**\n\n"
    keyboard = []

    for product in products:
        id_, name, desc, price, stock, cat, img, prescription = product
        status = "✅ In Stock" if stock > 0 else "❌ Out of Stock"
        prescription_text = " 🔒 Rx Required" if prescription else ""

        text += f"**{name}**{prescription_text}\n"
        text += f"💰 ${price:.2f} | {status}\n"
        text += f"📝 {desc}\n\n"

        if stock > 0:
            keyboard.append([InlineKeyboardButton(f"🛒 Add {name}", callback_data=f"add_to_cart_{id_}")])

    keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="browse_products")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Add to cart
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    user_id = update.effective_user.id

    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        await update.callback_query.answer("Product not found.")
        return

    if product[4] <= 0:  # stock
        await update.callback_query.answer("Product out of stock.")
        return

    # Add to cart
    cursor.execute('''
        INSERT OR REPLACE INTO cart (user_id, product_id, quantity)
        VALUES (?, ?, COALESCE((SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?), 0) + 1)
    ''', (user_id, product_id, user_id, product_id))
    db.conn.commit()

    await update.callback_query.answer(f"✅ {product[1]} added to cart!")

# Show cart
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT p.name, p.price, c.quantity, p.id
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,))

    cart_items = cursor.fetchall()

    if not cart_items:
        await update.message.reply_text("🛒 Your cart is empty!")
        return

    text = "🛒 **Your Cart**\n\n"
    total = 0
    keyboard = []

    for item in cart_items:
        name, price, quantity, product_id = item
        item_total = price * quantity
        total += item_total

        text += f"**{name}**\n"
        text += f"💰 ${price:.2f} x {quantity} = ${item_total:.2f}\n\n"

        keyboard.append([
            InlineKeyboardButton(f"➖", callback_data=f"decrease_{product_id}"),
            InlineKeyboardButton(f"{quantity}", callback_data=f"quantity_{product_id}"),
            InlineKeyboardButton(f"➕", callback_data=f"increase_{product_id}"),
            InlineKeyboardButton(f"🗑️", callback_data=f"remove_{product_id}")
        ])

    text += f"**Total: ${total:.2f}**"

    keyboard.append([InlineKeyboardButton("🛍️ Checkout", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🔙 Continue Shopping", callback_data="browse_products")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Checkout process
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Get cart items
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT p.name, p.price, c.quantity, p.requires_prescription
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,))

    cart_items = cursor.fetchall()

    if not cart_items:
        await update.callback_query.answer("Your cart is empty!")
        return

    # Check for prescription requirements
    prescription_required = any(item[3] for item in cart_items)

    text = "🛍️ **Checkout Summary**\n\n"
    total = 0

    for item in cart_items:
        name, price, quantity, prescription = item
        item_total = price * quantity
        total += item_total
        prescription_text = " 🔒" if prescription else ""
        text += f"{name}{prescription_text} x{quantity} - ${item_total:.2f}\n"

    text += f"\n**Total: ${total:.2f}**\n\n"

    if prescription_required:
        text += "⚠️ **Prescription Required**\n"
        text += "Some items in your cart require a valid prescription. You'll need to upload your prescription during the order process.\n\n"

    text += "📍 Please provide your delivery address and phone number to complete the order."

    keyboard = [
        [InlineKeyboardButton("📝 Provide Details", callback_data="provide_details")],
        [InlineKeyboardButton("🔙 Back to Cart", callback_data="show_cart")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Handle button callbacks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "browse_products":
        await browse_products(update, context)
    elif query.data.startswith("category_"):
        category = query.data.replace("category_", "")
        await show_category_products(update, context, category)
    elif query.data.startswith("add_to_cart_"):
        product_id = int(query.data.replace("add_to_cart_", ""))
        await add_to_cart(update, context, product_id)
    elif query.data == "checkout":
        await checkout(update, context)
    elif query.data == "provide_details":
        await query.edit_message_text(
            "📝 **Order Details**\n\n"
            "Please send me your delivery information in this format:\n\n"
            "**Address:** Your full delivery address\n"
            "**Phone:** Your contact number\n\n"
            "Example:\n"
            "Address: 123 Main St, City, State 12345\n"
            "Phone: +1-555-0123"
        )

# Handle text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛍️ Browse Products":
        await browse_products(update, context)
    elif text == "🛒 My Cart":
        await show_cart(update, context)
    elif text == "📋 My Orders":
        await show_orders(update, context)
    elif text == "📞 Contact Support":
        await update.message.reply_text(
            "📞 **Contact Support**\n\n"
            "For assistance, please contact us:\n"
            "📧 Email: support@pharmabot.com\n"
            "📱 Phone: +1-800-PHARMA\n"
            "🕒 Hours: 9 AM - 6 PM (Mon-Fri)\n\n"
            "We're here to help with your pharmaceutical needs!"
        )
    elif text == "ℹ️ About Us":
        await update.message.reply_text(
            "ℹ️ **About PharmaBot**\n\n"
            "We are a licensed pharmaceutical retailer committed to providing:\n\n"
            "✅ Genuine medications\n"
            "✅ Professional consultation\n"
            "✅ Fast, secure delivery\n"
            "✅ Regulatory compliance\n\n"
            "**License:** [Your License Number]\n"
            "**Established:** 2024\n\n"
            "Your health is our priority! 🏥"
        )

async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT id, products, total_amount, status, order_date
        FROM orders
        WHERE user_id = ?
        ORDER BY order_date DESC
        LIMIT 10
    ''', (user_id,))

    orders = cursor.fetchall()

    if not orders:
        await update.message.reply_text("📋 You have no orders yet.")
        return

    text = "📋 **Your Recent Orders**\n\n"

    for order in orders:
        order_id, products, total, status, date = order
        status_emoji = {"pending": "⏳", "confirmed": "✅", "shipped": "🚚", "delivered": "📦"}.get(status, "❓")

        text += f"**Order #{order_id}**\n"
        text += f"{status_emoji} Status: {status.title()}\n"
        text += f"💰 Total: ${total:.2f}\n"
        text += f"📅 Date: {date[:10]}\n\n"

    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("🤖 PharmaBot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()