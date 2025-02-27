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

from app.models import ContactSubmission
from datetime import datetime

from flask import render_template
from app.data import PROJECT_IDEAS

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import BlogPost
from app import db


from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import BlogPost, User, ContactSubmission
from app import db


from flask import jsonify, abort

from flask import send_file
from io import BytesIO
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, make_response, flash, abort, send_file

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

    # Add the logo
    if current_user.is_authenticated and current_user.logo:
        logo = Image(BytesIO(current_user.logo), width=2*inch, height=1*inch)
    else:
        logo_path = r"C:\Users\Admin\Pictures\txt\vecteezy_heart_1187381.png"
        logo = Image(logo_path, width=2*inch, height=1*inch)
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

    # Add company name if available
    if current_user.is_authenticated and current_user.company_name:
        elements.append(Paragraph(current_user.company_name, subtitle_style))

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

@bp.route('/subscribe')
def subscribe():
    return render_template('subscribe.html', title='Subscribe')

@bp.route('/about')
def about():
    return render_template('about.html', title='About')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        new_submission = ContactSubmission(
            name=name,
            email=email,
            message=message,
            submitted_at=datetime.utcnow()  # Explicitly set the current time
        )
        db.session.add(new_submission)
        db.session.commit()
        
        flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html', title='Contact Us')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Your account has been successfully deleted.')
    return redirect(url_for('main.index'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        company_name = request.form['company_name'] or None  # Set to None if empty
        user = User(email=email, company_name=company_name, is_admin=(email == 'admin@gmail.com'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
        else:
            user = User(email=email, company_name=company_name)
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
            if isinstance(items, dict):  # This is a category with sub-categories
                for subcategory, subitems in items.items():
                    for item in subitems:
                        quantity = int(request.form.get(f"{category}_{subcategory}_{item['name']}", 0))
                        if quantity > 0:
                            item_cost = item['price'] * quantity
                            total_cost += item_cost
                            items_data.append([f"{category} - {subcategory} - {item['name']}", quantity, item['price'], item_cost])
            else:  # This is a category without sub-categories
                for item in items:
                    quantity = int(request.form.get(f"{category}_{item['name']}", 0))
                    if quantity > 0:
                        item_cost = item['price'] * quantity
                        total_cost += item_cost
                        items_data.append([f"{category} - {item['name']}", quantity, item['price'], item_cost])

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

@bp.route('/update_company_name', methods=['POST'])
@login_required
def update_company_name():
    new_company_name = request.form.get('company_name', '').strip()
    current_user.company_name = new_company_name or None  # Set to None if empty
    db.session.commit()
    flash('Company name updated successfully')
    return redirect(url_for('main.account'))

@bp.route('/update_account', methods=['POST'])
@login_required
def update_account():
    current_user.company_name = request.form.get('company_name', '').strip() or None
    current_user.website = request.form.get('website', '').strip() or None
    current_user.business_email = request.form.get('business_email', '').strip() or None
    current_user.phone_number = request.form.get('phone_number', '').strip() or None
    
    db.session.commit()
    flash('Your account information has been updated successfully', 'success')
    return redirect(url_for('main.account'))

@bp.route('/custom-bidder', methods=['GET', 'POST'])
def custom_bidder():
    if request.method == 'POST':
        total_cost = 0
        items_data = []

        for category, items in CUSTOM_LANDSCAPE_ITEMS.items():
            if isinstance(items, dict):  # This is a category with sub-categories
                for subcategory, subitems in items.items():
                    for item in subitems:
                        quantity = int(request.form.get(f"{category}_{subcategory}_{item['name']}", 0))
                        if quantity > 0:
                            item_price = next((subitem['price'] for subitem in subitems if subitem['name'] == item['name']), item['price'])
                            item_cost = item_price * quantity
                            total_cost += item_cost
                            items_data.append([f"{category} - {subcategory} - {item['name']}", quantity, item_price, item_cost])
            else:  # This is a category without sub-categories
                for item in items:
                    quantity = int(request.form.get(f"{category}_{item['name']}", 0))
                    if quantity > 0:
                        item_price = next((i['price'] for i in items if i['name'] == item['name']), item['price'])
                        item_cost = item_price * quantity
                        total_cost += item_cost
                        items_data.append([f"{category} - {item['name']}", quantity, item_price, item_cost])

        if 'download_pdf' in request.form:
            if not items_data:
                return jsonify({'total_cost': total_cost})

            pdf_buffer = generate_pdf(items_data, total_cost, is_custom=True)
            response = make_response(pdf_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=custom_bid_estimate.pdf'
            return response

        return jsonify({'total_cost': total_cost})

    return render_template('custom_bidder.html', title='Custom Bidder', landscape_items=CUSTOM_LANDSCAPE_ITEMS)

@bp.route('/update-item-price', methods=['POST'])
def update_item_price_route():
    data = request.get_json()
    category = data.get('category')
    subcategory = data.get('subcategory')
    item_name = data.get('item_name')
    new_price = data.get('new_price')

    update_item_price(category, item_name, new_price, subcategory)
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

@bp.route('/upload_logo', methods=['POST'])
@login_required
def upload_logo():
    if 'logo' not in request.files:
        flash('No file part')
        return redirect(url_for('main.account'))
    file = request.files['logo']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('main.account'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        current_user.logo = file.read()
        current_user.logo_mimetype = file.mimetype
        db.session.commit()
        flash('Logo uploaded successfully')
    else:
        flash('Invalid file type')
    return redirect(url_for('main.account'))

@bp.route('/get_logo/<int:user_id>')
def get_logo(user_id):
    user = User.query.get_or_404(user_id)
    if user.logo:
        return send_file(
            BytesIO(user.logo),
            mimetype=user.logo_mimetype,
            as_attachment=False
        )
    else:
        abort(404)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




############################## Admin Routes #######################################

@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    
    users = User.query.all()
    contact_submissions = ContactSubmission.query.order_by(ContactSubmission.submitted_at.desc()).all()
    blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()

    if request.method == 'POST':
        if 'new_post' in request.form:
            title = request.form['title']
            content = request.form['content']
            post = BlogPost(title=title, content=content, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('New blog post created successfully!', 'success')
        elif 'edit_post' in request.form:
            post_id = request.form['post_id']
            post = BlogPost.query.get_or_404(post_id)
            post.title = request.form['title']
            post.content = request.form['content']
            db.session.commit()
            flash('Blog post updated successfully!', 'success')
        elif 'delete_post' in request.form:
            post_id = request.form['post_id']
            post = BlogPost.query.get_or_404(post_id)
            db.session.delete(post)
            db.session.commit()
            flash('Blog post deleted successfully!', 'success')
        return redirect(url_for('main.admin'))

    return render_template('admin.html', users=users, contact_submissions=contact_submissions, blog_posts=blog_posts)


@bp.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if current_user.is_admin:
        user = User.query.get_or_404(user_id)
        user.is_admin = not user.is_admin
        db.session.commit()
        return redirect(url_for('main.admin_panel'))
    else:
        abort(403)  # Forbidden

@bp.route('/admin/get_message/<int:submission_id>', methods=['GET'])
@login_required
def get_message(submission_id):
    if current_user.is_admin:
        submission = ContactSubmission.query.get_or_404(submission_id)
        return jsonify({
            'name': submission.name,
            'email': submission.email,
            'message': submission.message,
            'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        abort(403)  # Forbidden

@bp.route('/admin/delete_message/<int:submission_id>', methods=['POST'])
@login_required
def delete_message(submission_id):
    if current_user.is_admin:
        submission = ContactSubmission.query.get_or_404(submission_id)
        db.session.delete(submission)
        db.session.commit()
        return jsonify({'success': True})
    else:
        abort(403)  # Forbidden

@bp.route('/project-ideas')
def project_ideas():
    return render_template('project_ideas.html', project_ideas=PROJECT_IDEAS)












####################   BLog Routes #########################

@bp.route('/blog')
def blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog/index.html', posts=posts)

@bp.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('blog/post.html', post=post)

