from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.data import LANDSCAPE_ITEMS
from app.custom_data import CUSTOM_LANDSCAPE_ITEMS, save_custom_data, remove_custom_item, reset_custom_data

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html', title='Home')

@bp.route('/about')
def about():
    return render_template('about.html', title='About')

@bp.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Us')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('main.index'))
        else:
            return render_template('login.html', title='Login', error='Invalid credentials')
    
    return render_template('login.html', title='Login')

@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.index'))

@bp.route('/signup')
def signup():
    return render_template('signup.html', title='Sign Up')

@bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html', title='Forgot Password')

@bp.route('/bid-estimator', methods=['GET', 'POST'])
def bid_estimator():
    if request.method == 'POST':
        total_cost = 0
        for category, items in LANDSCAPE_ITEMS.items():
            for item in items:
                quantity = int(request.form.get(f"{category}_{item['name']}", 0))
                total_cost += item['price'] * quantity
        return jsonify({'total_cost': total_cost})
    
    return render_template('bid_estimator.html', title='Bid Estimator', landscape_items=LANDSCAPE_ITEMS, total_cost=0)

@bp.route('/custom-bidder', methods=['GET', 'POST'])
def custom_bidder():
    if request.method == 'POST':
        total_cost = 0
        for category, items in CUSTOM_LANDSCAPE_ITEMS.items():
            for item in items:
                quantity = int(request.form.get(f"{category}_{item['name']}", 0))
                total_cost += item['price'] * quantity
        return jsonify({'total_cost': total_cost})
    
    return render_template('custom_bidder.html', title='Custom Bidder', landscape_items=CUSTOM_LANDSCAPE_ITEMS, total_cost=0)

@bp.route('/add-custom-item', methods=['POST'])
def add_custom_item():
    category = request.form.get('category')
    name = request.form.get('name')
    price = float(request.form.get('price'))

    if category not in CUSTOM_LANDSCAPE_ITEMS:
        CUSTOM_LANDSCAPE_ITEMS[category] = []

    CUSTOM_LANDSCAPE_ITEMS[category].append({'name': name, 'price': price})
    save_custom_data(CUSTOM_LANDSCAPE_ITEMS)

    return redirect(url_for('main.custom_bidder'))

@bp.route('/reset-custom-data')
def reset_custom_data_route():
    reset_custom_data()
    return redirect(url_for('main.custom_bidder'))

@bp.route('/remove-custom-item/<category>/<item_name>')
def remove_custom_item_route(category, item_name):
    remove_custom_item(category, item_name)
    return redirect(url_for('main.custom_bidder'))