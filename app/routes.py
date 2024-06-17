from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.data import LANDSCAPE_ITEMS
from app.custom_data import CUSTOM_LANDSCAPE_ITEMS, save_custom_data, remove_custom_item, reset_custom_data

import json
from flask import jsonify
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


from io import BytesIO
from flask import make_response, jsonify
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from app.data import LANDSCAPE_ITEMS


from io import BytesIO
from flask import make_response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

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
                # No items selected, return JSON response
                return jsonify({'total_cost': total_cost})

            # Create a BytesIO object to store the PDF data
            pdf_buffer = BytesIO()

            # Create a SimpleDocTemplate object with the BytesIO buffer
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)

            # Get the sample style sheet
            styles = getSampleStyleSheet()

            # Define custom styles
            title_style = ParagraphStyle(
                name='TitleStyle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.darkgreen,
                alignment=1,
                spaceAfter=0.3 * inch
            )
            subtitle_style = ParagraphStyle(
                name='SubtitleStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.darkblue,
                alignment=1,
                spaceAfter=0.2 * inch
            )
            table_header_style = ParagraphStyle(
                name='TableHeaderStyle',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.white,
                alignment=1
            )
            table_cell_style = ParagraphStyle(
                name='TableCellStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black
            )
            total_cost_style = ParagraphStyle(
                name='TotalCostStyle',
                parent=styles['Normal'],
                fontSize=16,
                textColor=colors.darkgreen,
                alignment=2,
                spaceAfter=0.3 * inch
            )
            thank_you_style = ParagraphStyle(
                name='ThankYouStyle',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.black,
                alignment=1
            )

            # Create the document elements
            elements = []

            # Add the company logo
            logo_path = r"C:\Users\Admin\Pictures\txt\vecteezy_heart_1187381.png"
            logo = Image(logo_path, width=2 * inch, height=1 * inch)
            logo.hAlign = 'LEFT'
            elements.append(logo)

            # Add the title
            elements.append(Paragraph('Landscape Bid Estimate', title_style))

            # Add the subtitle
            elements.append(Paragraph('Selected Items', subtitle_style))

            # Create a Table object with the selected items and their costs
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
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)

            # Add a spacer
            elements.append(Spacer(1, 0.3 * inch))

            # Add the total cost
            total_cost_text = f'Total Estimated Cost: ${total_cost:.2f}'
            elements.append(Paragraph(total_cost_text, total_cost_style))

            # Add a spacer
            elements.append(Spacer(1, 0.2 * inch))

            # Add a thank you paragraph
            thank_you_text = "Thank you for considering our services. We look forward to working with you on your landscape project. If you have any questions or would like to proceed with the estimate, please feel free to contact us."
            elements.append(Paragraph(thank_you_text, thank_you_style))

            # Build the PDF document
            doc.build(elements)

            # Create a response with the PDF data
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