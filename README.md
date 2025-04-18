**ShopSmart – Flask-Based eCommerce Platform**
ShopSmart is a simple yet powerful eCommerce web application built using Python (Flask), HTML/CSS, and Bootstrap. It supports user registration, login, product browsing, cart management, purchase history, and product recommendations.

**Features**
👤 User Authentication (Signup, Login, Logout)
🛍️ Product Listing with Categories and Images
🛒 Add to Cart & Cart Management
💳 Purchase Flow and Purchase History
⭐ Product Ratings & Reviews
🔍 Search and Smart Recommendations
📈 Popularity-based and Category-based Recommendations
🔐 User sessions with Flask session

**Tech Stack**
Backend: Python 3.12, Flask
Frontend: HTML, CSS, Bootstrap 5, Tailwind (used in login/signup)
Templating: Jinja2
Data: JSON files for products and users
Persistent Storage: users.txt and final_products_with_images.json

**Getting Started**
1. Clone the Repo
git clone https://github.com/yourusername/shopsmart.git
cd shopsmart
2. Install Dependencies
Make sure you're using Python 3.12+
pip install flask
3. Run the App
python app.py
Visit: http://127.0.0.1:5000

📁 File Structure
.
├── app.py                  # Main Flask application
├── users.txt               # User data (purchases, ratings, cart)
├── final_products_with_images.json  # Product database
├── templates/
│   ├── base.html
│   ├── navbar.html
│   ├── products.html
│   ├── cart.html
│   ├── history.html
│   ├── login.html
│   └── signup.html
├── static/
│   └── style.css           # Custom CSS styling

**📝 Notes**
Product data is loaded from a JSON file (final_products_with_images.json)
Cart items are saved per user in users.txt
No external database required (but can be upgraded later to SQLite/PostgreSQL)

**📌 TODO (Optional Enhancements)**
 Add product categories and filters
 Add admin dashboard for managing inventory
 Add support for payments / checkout
 Replace file-based storage with a database
 Enhancement of recommendation logic using AI/ML
 


