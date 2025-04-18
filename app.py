from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'secret_key_here'

class User:
    def __init__(self, password, purchases=None, ratings=None, cart=None):
        self.password = password
        self.purchases = purchases if purchases else []
        self.ratings = ratings if ratings else {}
        self.cart = cart if cart else []  # Add cart attribute

class Product:
    def __init__(self, id, title, price, category, image, purchase_count=0, rating=0.0, rating_count=0):
        self.id = id
        self.title = title
        self.price = price
        self.category = category
        self.image = image
        self.purchase_count = purchase_count
        self.rating = rating
        self.rating_count = rating_count

users = {}
products = {}
similarity_graph = defaultdict(list)

def load_users():
    global users
    users = {}
    try:
        with open("users.txt", "r") as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 4:  # Handle old and new data formats
                    username = parts[0]
                    password = parts[1]
                    purchases = json.loads(parts[2]) if parts[2] else []
                    ratings = json.loads(parts[3]) if parts[3] else {}
                    # Handle cart for old users (default to empty list)
                    cart = json.loads(parts[4]) if len(parts) >= 5 else []
                    users[username] = User(
                        password=password,
                        purchases=purchases,
                        ratings=ratings,
                        cart=cart
                    )
    except Exception as e:
        print(f"Error loading users: {str(e)}")

# Update save_users() in app.py
def save_users():
    with open("users.txt", "w") as f:
        for username, user in users.items():
            line = f"{username}\t{user.password}\t{json.dumps(user.purchases)}\t{json.dumps(user.ratings)}\t{json.dumps(user.cart)}\n"
            f.write(line)

def load_products():
    global products
    products = {}
    if not os.path.exists("final_products_with_images.json"):
        return
    try:
        with open("final_products_with_images.json") as f:
            data = json.load(f)
            for p in data:
                try:
                    product = Product(
                        id=str(p.get("product_id", "")),
                        title=p.get("product_title", ""),
                        price=float(p.get("price", 0.0)),
                        category=p.get("category", ""),
                        image=p.get("image", ""),
                        purchase_count=int(p.get("purchase_count", 0)),
                        rating=float(p.get("rating", 0.0)),
                        rating_count=int(p.get("rating_count", 0))
                    )
                    products[product.id] = product
                except Exception as e:
                    print(f"Product error: {str(e)}")
    except Exception as e:
        print(f"Error loading products: {str(e)}")

def generate_similarity_graph():
    global similarity_graph
    similarity_graph = defaultdict(list)
    category_map = defaultdict(list)
    for p in products.values():
        category_map[p.category].append(p.id)
    for p in products.values():
        similarity_graph[p.id] = [pid for pid in category_map[p.category] if pid != p.id]

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('products_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username in users and users[username].password == password:
            session['user'] = username
            return redirect(url_for('products_page'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            if not username or not password:
                return render_template('signup.html', error='Username and password are required')

            if username in users:
                return render_template('signup.html', error='Username already exists')

            users[username] = User(password=password)
            save_users()
            return redirect(url_for('login'))

        except Exception as e:
            print(f"SIGNUP ERROR: {str(e)}")
            return render_template('signup.html', error='Registration failed. Please try again.')

    return render_template('signup.html')



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/products')
def products_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('products.html', products=products.values(), user=session.get('user'))

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in products.values() if query in p.title.lower()]
    return render_template('products.html', products=results, user=session.get('user'))

@app.route('/recommendations')
def recommendations():
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))
    purchased = set(p['product_id'] for p in users[username].purchases)
    sorted_products = sorted(products.values(), key=lambda p: -p.purchase_count)
    recs = [p for p in sorted_products if p.id not in purchased and p.purchase_count > 0]
    return render_template('products.html', products=recs, user=username)

# Modify add_to_cart() in app.py
@app.route('/add_to_cart/<product_id>')
def add_to_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    users[username].cart.append(product_id)
    save_users()  # Save the updated cart
    return '', 204

@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']
    if username not in users:
        session.pop('user', None)
        return redirect(url_for('login'))
    
    user = users[username]
    
    if request.method == 'POST':
        product_id = request.form.get('remove')
        try:
            user.cart.remove(product_id)  # Remove first occurrence
            save_users()
        except ValueError:
            pass  # If product_id not found, do nothing
    
    # Process cart items from user.cart
    quantities = defaultdict(int)
    for pid in user.cart:
        quantities[pid] += 1
    
    cart_items = []
    for pid, qty in quantities.items():
        if pid in products:
            product = products[pid]
            cart_items.append({
                'product': product,
                'quantity': qty,
                'total': product.price * qty
            })
    
    return render_template('cart.html',
                         cart_items=cart_items,
                         grand_total=sum(item['total'] for item in cart_items))

@app.route('/rate/<product_id>', methods=['POST'])
def rate_product(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    rating = request.form.get('rating')
    if rating and product_id in products:
        users[username].ratings[product_id] = int(rating)
        product = products[product_id]
        product.rating_count += 1
        product.rating = ((product.rating * (product.rating_count - 1)) + int(rating)) / product.rating_count
        save_users()
    return redirect(url_for('history'))

@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']
    if username not in users:
        session.pop('user', None)
        return redirect(url_for('login'))
    
    user = users[username]
    purchased_products = []
    
    for purchase in user.purchases:
        pid = purchase['product_id']
        if pid in products:
            purchased_products.append({
                'product': products[pid],
                'purchase_date': purchase.get('date', 'N/A'),
                'amount': purchase['amount'],
                # Add rating information directly to the purchase
                'user_rating': user.ratings.get(pid, None)
            })
    
    return render_template('history.html',
                         purchases=purchased_products,
                         total_spent=sum(p['amount'] for p in user.purchases))

@app.route('/purchase/<product_id>')
def purchase(product_id):
    username = session.get('user')
    if not username or product_id not in products:
        return redirect(url_for('products_page'))
    product = products[product_id]
    users[username].purchases.append({
        'product_id': product_id,
        'amount': product.price,
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    product.purchase_count += 1
    save_users()
    return redirect(url_for('history'))

# Add to app.py
@app.context_processor
def inject_user_data():
    if 'user' in session:
        username = session['user']
        user = users.get(username)
        if user:
            return {
                'current_user': username,
                'cart_count': len(user.cart)
            }
    return {'current_user': None, 'cart_count': 0}

if __name__ == '__main__':
    load_users()
    load_products()
    generate_similarity_graph()
    app.run(debug=True)