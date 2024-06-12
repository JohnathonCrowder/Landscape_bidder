from flask import Blueprint, render_template, request
from app.data import LANDSCAPE_ITEMS

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html', title='Home')

@bp.route('/about')
def about():
    return render_template('about.html', title='About')

# New route for the contact page
@bp.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Us')

@bp.route('/bid-estimator', methods=['GET', 'POST'])
def bid_estimator():
    if request.method == 'POST':
        total_cost = 0
        for category, items in LANDSCAPE_ITEMS.items():
            for item in items:
                quantity = int(request.form.get(f"{category}_{item['name']}", 0))
                total_cost += item['price'] * quantity

        return render_template('bid_estimator.html', title='Bid Estimator', landscape_items=LANDSCAPE_ITEMS, total_cost=total_cost)
    
    return render_template('bid_estimator.html', title='Bid Estimator', landscape_items=LANDSCAPE_ITEMS, total_cost=0)