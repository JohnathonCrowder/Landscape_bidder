from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, make_response
from app.data import LANDSCAPE_ITEMS
from app.custom_data import CUSTOM_LANDSCAPE_ITEMS, save_custom_data, remove_custom_item, reset_custom_data, update_item_price
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import User
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable

bp = Blueprint('main', __name__)

def generate_pdf(items_data, total_cost, is_custom=False):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2f855a'),
        alignment=1,
        spaceAfter=0.5 * inch
    )
    subtitle_style = ParagraphStyle(
        name='SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#2c5282'),
        alignment=1,
        spaceAfter=0.3 * inch
    )
    table_header_style = ParagraphStyle(
        name='TableHeaderStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.white,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    table_cell_style = ParagraphStyle(
        name='TableCellStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        fontName='Helvetica'
    )
    total_cost_style = ParagraphStyle(
        name='TotalCostStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#2f855a'),
        alignment=2,
        spaceAfter=0.5 * inch
    )
    thank_you_style = ParagraphStyle(
        name='ThankYouStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        alignment=1
    )

    elements = []

    # Add the company logo
    logo_path = r"C:\Users\Admin\Pictures\txt\vecteezy_heart_1187381.png"
    logo = Image(logo_path, width=2 * inch, height=1 * inch)
    logo.hAlign = 'CENTER'
    logo_table = Table([[logo]], colWidths=[doc.width])
    logo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5 * inch),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5 * inch),
    ]))
    elements.append(logo_table)

    # Add the title
    elements.append(Spacer(1, 0.2 * inch))
    if is_custom:
        elements.append(Paragraph('Custom Landscape Bid Estimate', title_style))
    else:
        elements.append(Paragraph('Landscape Bid Estimate', title_style))

    elements.append(HRFlowable(width='100%', color=colors.HexColor('#2f855a'), thickness=2, spaceAfter=0.3 * inch))
    elements.append(Paragraph('Selected Items', subtitle_style))

    table_data = [['Item', 'Quantity', 'Price', 'Cost']]
    for item in items_data:
        row = [
            Paragraph(str(item[0]), table_cell_style),
            Paragraph(str(item[1]), table_cell_style),
            Paragraph(f'${item[2]:.2f}', table_cell_style),
            Paragraph(f'${item[3]:.2f}', table_cell_style)
        ]
        table_data.append(row)

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2f855a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fff4')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2f855a'))
    ]))
    elements.append(table)

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f'Total Estimated Cost: ${total_cost:.2f}', total_cost_style))
    elements.append(HRFlowable(width='100%', color=colors.HexColor('#2f855a'), thickness=1, spaceAfter=0.2 * inch))

    thank_you_text = "Thank you for considering our services. We look forward to working with you on your landscape project. If you have any questions or would like to proceed with the estimate, please feel free to contact us."
    elements.append(Paragraph(thank_you_text, thank_you_style))

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer

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
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('main.index'))
    return render_template('signup.html')

@bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html', title='Forgot Password')

@bp.route('/bid-estimator', methods=['GET', 'POST'])
def bid_estimator():
    if request.method == 'POST':
        total_cost = 0
        items_data = []

        for category, items in LANDSCAPE_ITEMS.items():
            for item in items:
                quantity = request.form.get(f"{category}_{item['name']}", 0)
                if int(quantity) > 0:
                    item_cost = item['price'] * int(quantity)
                    total_cost += item_cost
                    items_data.append([item['name'], int(quantity), item['price'], item_cost])

        if 'download_pdf' in request.form:
            if not items_data:
                return jsonify({'total_cost': total_cost})

            pdf_buffer = generate_pdf(items_data, total_cost)
            response = make_response(pdf_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=bid_estimate.pdf'
            return response

        return jsonify({'total_cost': total_cost})

    return render_template('bid_estimator.html', items=LANDSCAPE_ITEMS)

@bp.route('/custom-bidder', methods=['GET', 'POST'])
def custom_bidder():
    if request.method == 'POST':
        total_cost = 0
        items_data = []

        for category, items in CUSTOM_LANDSCAPE_ITEMS.items():
            for item in items:
                quantity = int(request.form.get(f"{category}_{item['name']}", 0))
                if quantity > 0:
                    item_cost = item['price'] * quantity
                    total_cost += item_cost
                    items_data.append([item['name'], quantity, item['price'], item_cost])

        if 'download_pdf' in request.form:
            pdf_buffer = generate_pdf(items_data, total_cost, is_custom=True)
            response = make_response(pdf_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=custom_bid_estimate.pdf'
            return response

        return jsonify({'total_cost': total_cost})
    
    return render_template('custom_bidder.html', title='Custom Bidder', landscape_items=CUSTOM_LANDSCAPE_ITEMS)

@bp.route('/update-item-price', methods=['POST'])
def update_item_price_route():
    category = request.form.get('category')
    item_name = request.form.get('item_name')
    new_price = float(request.form.get('new_price'))
    
    update_item_price(category, item_name, new_price)
    return jsonify({'success': True})

@bp.route('/account')
@login_required
def account():
    return render_template('account.html')

@bp.route('/add-custom-item', methods=['POST'])
def add_custom_item():
    global CUSTOM_LANDSCAPE_ITEMS
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
    global CUSTOM_LANDSCAPE_ITEMS
    CUSTOM_LANDSCAPE_ITEMS = reset_custom_data()
    return redirect(url_for('main.custom_bidder'))

@bp.route('/remove-custom-item/<category>/<item_name>')
def remove_custom_item_route(category, item_name):
    remove_custom_item(category, item_name)
    return redirect(url_for('main.custom_bidder'))