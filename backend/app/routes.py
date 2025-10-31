import requests
from utilities import admin_required
from datetime import datetime, timezone
from app import app, db, paychangu_client
from flask import request, jsonify, redirect, current_app
from paychangu.models.payment import Payment as PaychanguPayment
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Users, Abstracts, Payments, Invoices, Contact, Notifications, Feedback, Reviews
from app.email_service import (
    send_abstract_confirmation_email, 
    send_payment_confirmation_email,
    send_abstract_review_email,
    send_admin_notification_email,
    send_contact_confirmation_email,
    send_contact_admin_notification_email
)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/api/submit", methods=["POST"])
@login_required
def submit_abstract():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    title = data.get("title")
    content = data.get("content")
    field = data.get("field")
    country = data.get("country")
    year = data.get("year")
    institution = data.get("institution")

    if not all([title, content, field, institution, country, year]):
        return jsonify({"error": "Missing required fields"}), 400

    allowed_fields = ['Public Health', 'AI', 'Technology', 'Agriculture', 'Mining Engineering']
    if data['field'].lower() not in [f.lower() for f in allowed_fields]:
        return jsonify({"error": "Invalid field"}), 400

    abstract = Abstracts(
        title = title,
        content = content,
        field = field,
        year = year,
        country = country,
        institution = institution,
        author_id = current_user.id
    )
    
    try:
        db.session.add(abstract)
        db.session.commit()
        
        # Send confirmation email to user
        send_abstract_confirmation_email(
            user_email=current_user.email,
            user_name=current_user.fullname,
            abstract_title=abstract.title,
            abstract_id=abstract.id
        )
        
        # Send notification email to admin
        send_admin_notification_email(
            abstract_title=abstract.title,
            author_name=current_user.fullname,
            abstract_id=abstract.id
        )
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Abstract submitted successfully", "id": abstract.id}), 201


@app.route("/api/abstracts", methods=["GET"])
def get_abstracts():
    abstracts = Abstracts.query.all()
    if not abstracts:
        return jsonify({"error": "No abstracts found"}), 404
    return jsonify([{
    "id": abstract.id,
    "title": abstract.title,
    "content": abstract.content,
    "field": abstract.field,
    "institution": abstract.institution,
    "yearOfResearch": abstract.year,
    "keywords": abstract.keywords,
    "status": abstract.status,
    "authorId": abstract.author_id,
    "dateSubmitted": abstract.date_submitted.isoformat()
} for abstract in abstracts]), 200


@app.route("/api/abstracts/search", methods=["GET"])
def search_abstracts():
    """Search abstracts with filters"""
    # Get query parameters
    field = request.args.get('field')
    country = request.args.get('country')
    institution = request.args.get('institution')
    year = request.args.get('year', type=int)
    keyword = request.args.get('keyword')
    
    # Build query
    query = Abstracts.query.filter_by(status='published')
    
    if field:
        query = query.filter_by(field=field)
    if country:
        query = query.filter_by(country=country)
    if institution:
        query = query.filter(Abstracts.institution.ilike(f'%{institution}%'))
    if year:
        query = query.filter_by(year=year)
    if keyword:
        query = query.filter(
            db.or_(
                Abstracts.title.ilike(f'%{keyword}%'),
                Abstracts.content.ilike(f'%{keyword}%'),
                Abstracts.keywords.ilike(f'%{keyword}%')
            )
        )
    
    abstracts = query.all()
    
    # Return empty list if no results (not an error)
    return jsonify([{
        "id": abstract.id,
        "title": abstract.title,
        "content": abstract.content,
        "field": abstract.field,
        "institution": abstract.institution,
        "country": abstract.country,
        "yearOfResearch": abstract.year,
        "keywords": abstract.keywords,
        "status": abstract.status,
        "authorId": abstract.author_id,
        "dateSubmitted": abstract.date_submitted.isoformat()
    } for abstract in abstracts]), 200


@app.route("/api/abstracts/<int:id>", methods=["GET"])
def get_specific_abstract(id):
    abstract = Abstracts.query.get(id)
    
    if abstract is None:
        return jsonify({"error": "Abstract not found"}), 404
    
    return jsonify({
        "id": abstract.id,
        "title": abstract.title,
        "content": abstract.content,
        "field": abstract.field,
        "institution": abstract.institution,
        "yearOfResearch": abstract.year,
        "keywords": abstract.keywords,
        "status": abstract.status,
        "authorId": abstract.author_id,
        "dateSubmitted": abstract.date_submitted.isoformat()
    }), 200


@app.route("/api/admin", methods=["GET"])
@admin_required
def admin_dashboard():
    """Get admin dashboard with overview statistics"""
    # Get all abstracts with counts by status
    abstracts = Abstracts.query.all()

    stats = {
        "totalAbstracts": len(abstracts),
        "pendingAbstracts": len([a for a in abstracts if a.status == "pending"]),
        "approvedAbstracts": len([a for a in abstracts if a.status == "approved"]),
        "rejectedAbstracts": len([a for a in abstracts if a.status == "rejected"]),
        "totalUsers": Users.query.count(),
        "totalPayments": Payments.query.filter_by(status="confirmed").count(),
        "pendingPayments": Payments.query.filter_by(status="pending").count()
    }

    # Get recent abstracts for review
    recent_abstracts = Abstracts.query.filter_by(status="pending").order_by(Abstracts.date_submitted.desc()).limit(10).all()
    recent_abstracts_data = [{
        "id": abstract.id,
        "title": abstract.title,
        "field": abstract.field,
        "institution": abstract.institution,
        "author": abstract.author.fullname,
        "dateSubmitted": abstract.date_submitted.isoformat()
    } for abstract in recent_abstracts]

    return jsonify({
        "stats": stats,
        "recentAbstracts": recent_abstracts_data
    }), 200


@app.route("/api/payments/initiate", methods=["POST"])
@login_required
def initiate_payment():
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    abstract_id = data.get("abstract_id")
    amount = data.get("amount", 1.99)
    currency = data.get("currency", "USD")
    method = data.get("method", "PayChangu")  # Default to PayChangu
    if not abstract_id:
        return jsonify({"error": "Missing abstract_id"}), 400

    # Check if abstract exists
    abstract = Abstracts.query.get(abstract_id)
    if not abstract:
        return jsonify({"error": "Abstract not found"}), 404

    # Initiate PayChangu payment
    paychangu_payment = PaychanguPayment(
        amount=amount,
        currency=currency,
        email=current_user.email,
        first_name=current_user.firstname,
        last_name=current_user.lastname,
        callback_url=f"{current_app.config['PAYCHANGU_CALLBACK_URL']}",
        return_url=f"{current_app.config['WEBSITE_URL']}/api/user/dashboard",
        tx_ref=f"abstract_{abstract_id}_{int(datetime.now().timestamp())}",
        customization={
            "title": "African Research Hub Abstract Payment",
            "description": f"Payment for publishing abstract ID {abstract_id}"
        }
    )

    response = paychangu_client.initiate_transaction(paychangu_payment)

    if response.status != 'success':
        return jsonify({"error": "Failed to initiate payment"}), 500

    payment_link = response.data.checkout_url
    transaction_id =  response.data.tx_ref

    # Create Payment
    payment = Payments(
        abstract_id = abstract_id,
        amount = amount,
        currency = currency,
        method = method,
        transaction_id = transaction_id,
        payment_link = payment_link
    )
    
    # Generate payment link from PayChangu
    invoice_url = payment.payment_link

    # Create Invoice
    invoice = Invoices(
        abstract_id = abstract_id,
        invoice_url = invoice_url,
    )

    try:
        db.session.add_all([invoice, payment])
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Invoice and payment initiated",
        "invoiceId": invoice.id,
        "invoiceUrl": invoice.invoice_url,
        "paymentId": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
        "method": payment.method
    }), 201


@app.route("/api/payments/confirm", methods=["POST"])
def confirm_payment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    payment_id = data.get("payment_id")
    if not payment_id:
        return jsonify({"error": "Missing payment_id"}), 400

    payment = Payments.query.get(payment_id)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    # Get abstract and user info for email
    abstract = Abstracts.query.get(payment.abstract_id)
    user = Users.query.get(abstract.author_id)

    # Update payment status, date, and invoice paid status
    payment.status = "confirmed"
    payment.payment_date = datetime.now(timezone.utc)

    # Publish abstract after payment
    abstract.status = 'published'

    abstract_id = payment.abstract_id
    invoice = Invoices.query.filter_by(abstract_id=abstract_id).first()

    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    invoice.paid = True

    try:
        db.session.commit()
        
        # Send payment confirmation email
        send_payment_confirmation_email(
            user_email=user.email,
            user_name=user.fullname,
            amount=payment.amount,
            currency=payment.currency,
            invoice_id=invoice.id
        )
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Payment confirmed",
        "payment_id": payment.id,
        "status": payment.status,
        "payment_date": payment.payment_date.isoformat()
    }), 200


@app.route("/api/login", methods=["POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role in ["Admin", "admin"]:
            return redirect("/api/admin")
        return redirect("/api/user/dashboard")

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    user = Users.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Email not found"}), 401

    elif user.verify_password(password) == False:
        return jsonify({"error": "Invalid password"}), 401

    if user.role in ["Admin", "admin"]:
        login_user(user)
        return redirect("/api/admin")

    elif user.role in ["Student", "student"]:
        login_user(user)
        return redirect("/api/user/dashboard")

    return jsonify({"message": "You have been successfully logged in"}), 201


@app.route("/api/register", methods=["POST"])
def register():
    if current_user.is_authenticated:
        if current_user.role in ["Admin", "admin"]:
            return redirect("/api/admin")
        return redirect("/api/user/dashboard")

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    fullname = data.get("fullname")
    email = data.get("email")
    country = data.get("country")
    password = data.get("password")
    role = data.get("role")

    if not all([fullname, email, country, password, role]):
        return jsonify({"error": "Missing required fields"}), 400

    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = Users(
        fullname = fullname,
        email = email,
        country = country,
        role = role
    )
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": f"Account created successfully, role: {user.role}"}), 201


@app.route('/api/logout/', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "You have been logged out"}), 200


@app.route("/api/contact/", methods=["POST"])
def contact():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not all([name, email, message]):
        return jsonify({"error": "Missing required fields: name, email, and message"}), 400

    # Basic email validation
    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400

    # Validate message length
    if len(message.strip()) < 10:
        return jsonify({"error": "Message must be at least 10 characters long"}), 400

    if len(message) > 2000:
        return jsonify({"error": "Message must be less than 2000 characters"}), 400

    # Validate name length
    if len(name.strip()) < 2:
        return jsonify({"error": "Name must be at least 2 characters long"}), 400

    contact = Contact(
        name = name.strip(),
        email = email.strip().lower(),
        message = message.strip()
    )

    try:
        db.session.add(contact)
        db.session.commit()
        
        # Send confirmation email to the user
        send_contact_confirmation_email(
            user_email=contact.email,
            user_name=contact.name
        )
        
        # Send notification email to admin
        send_contact_admin_notification_email(
            contact_name=contact.name,
            contact_email=contact.email,
            contact_message=contact.message,
            contact_id=contact.id
        )
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to process contact form: {str(e)}"}), 500

    return jsonify({
        "message": "Thank you for your message! We'll get back to you within 24-48 hours.", 
        "id": contact.id
    }), 201


@app.route("/api/user/dashboard", methods=["GET"])
@login_required
def user_dashboard():
    """Get student's dashboard info including their abstracts and payment status"""
    
    if current_user.role == 'admin':
        return jsonify({"error": "Student access required"}), 403

    # Get user's abstracts with related payment/invoice info
    user_abstracts = []
    for abstract in current_user.abstracts:
        # Get payment info for this abstract
        payment = Payments.query.filter_by(abstract_id=abstract.id).first()
        invoice = Invoices.query.filter_by(abstract_id=abstract.id).first()

        abstract_data = {
            "id": abstract.id,
            "title": abstract.title,
            "content": abstract.content,
            "field": abstract.field,
            "institution": abstract.institution,
            "country": abstract.country,
            "year": abstract.year,
            "keywords": abstract.keywords,
            "status": abstract.status,
            "dateSubmitted": abstract.date_submitted.isoformat(),
            "paymentStatus": payment.status if payment else "not_initiated",
            "paymentAmount": payment.amount if payment else None,
            "invoicePaid": invoice.paid if invoice else False,
            "invoiceUrl": invoice.invoice_url if invoice else None
        }
        user_abstracts.append(abstract_data)

    # Get user's notifications
    notifications = Notifications.query.filter_by(user_id=current_user.id).order_by(Notifications.id.desc()).all()
    notification_data = [{
        "id": notification.id,
        "message": notification.message,
        "read": notification.read
    } for notification in notifications]

    dashboard_data = {
        "user": {
            "id": current_user.id,
            "fullname": current_user.fullname,
            "email": current_user.email,
            "country": current_user.country,
            "role": current_user.role
        },
        "abstracts": user_abstracts,
        "notifications": notification_data,
        "stats": {
            "totalAbstracts": len(user_abstracts),
            "pendingAbstracts": len([a for a in user_abstracts if a["status"] == "pending"]),
            "approvedAbstracts": len([a for a in user_abstracts if a["status"] == "approved"]),
            "rejectedAbstracts": len([a for a in user_abstracts if a["status"] == "rejected"]),
            "unreadNotifications": len([n for n in notifications if not n.read])
        }
    }

    return jsonify(dashboard_data), 200


@app.route("/api/admin/review/<int:abstract_id>", methods=["POST"])
@admin_required
def review_abstract(abstract_id):
    """Admin endpoint to approve/reject abstract with feedback"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    action = data.get("action")  # "approve" or "reject"
    admin_id = current_user.id
    feedback_comment = data.get("feedback", "")

    if not all([action]):
        return jsonify({"error": "Missing required field: action"}), 400

    if action not in ["approve", "reject"]:
        return jsonify({"error": "Action must be 'approve' or 'reject'"}), 400

    # Verify admin exists and has admin role
    admin = Users.query.get(admin_id)

    if not admin or admin.role != "admin":
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    abstract = Abstracts.query.get(abstract_id)
    
    if abstract is None:
        return jsonify({"error": "Abstract not found"}), 404
    
    user = Users.query.get(abstract.author_id)

    # Update abstract status
    if action == "approve":
        abstract.status = "approved"
        notification_message = f"Your abstract '{abstract.title}' has been approved!"
    else:
        abstract.status = "rejected"
        notification_message = f"Your abstract '{abstract.title}' has been rejected. Please check feedback."

    try:
        # Add feedback if provided
        if feedback_comment:
            feedback = Feedback(
                abstract_id = abstract_id,
                admin_id = admin_id,
                comment = feedback_comment
            )
            db.session.add(feedback)

        # Add notification for the author
        notification = Notifications(
            user_id = abstract.author_id,
            message = notification_message
        )

        db.session.add(notification)
        db.session.commit()
        
        # Send email notification to user
        send_abstract_review_email(
            user_email=user.email,
            user_name=user.fullname,
            abstract_title=abstract.title,
            status=abstract.status,
            feedback=feedback_comment if feedback_comment else None
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": f"Abstract {action}d",
        "abstractId": abstract.id,
        "status": abstract.status,
        "feedbackProvided": bool(feedback_comment)
    }), 200


@app.route("/api/resubmit/<int:abstract_id>", methods=["POST"])
def resubmit_abstract(abstract_id):
    """Allow students to update and resubmit rejected abstracts"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    abstract = Abstracts.query.get(abstract_id)
    if abstract is None:
        return jsonify({"error": "Abstract not found"}), 404

    # Verify the user owns this abstract
    if abstract.author_id != user_id:
        return jsonify({"error": "Unauthorized: You can only resubmit your own abstracts"}), 403

    # Only allow resubmission of rejected abstracts
    if abstract.status != "rejected":
        return jsonify({"error": "Only rejected abstracts can be resubmitted"}), 400

    # Update abstract fields if provided
    if "title" in data:
        abstract.title = data["title"]
    if "content" in data:
        abstract.content = data["content"]
    if "field" in data:
        abstract.field = data["field"]
    if "institution" in data:
        abstract.institution = data["institution"]
    if "country" in data:
        abstract.country = data["country"]
    if "year" in data:
        abstract.year = data["year"]
    if "keywords" in data:
        abstract.keywords = data["keywords"]

    # Reset status to pending and update submission date
    abstract.status = "pending"
    abstract.date_submitted = datetime.now(timezone.utc)

    try:
        # Add notification for successful resubmission
        notification = Notifications(
            user_id = user_id,
            message = f"Your abstract '{abstract.title}' has been resubmitted successfully!"
        )
        db.session.add(notification)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Abstract resubmitted successfully",
        "abstractId": abstract.id,
        "status": abstract.status,
        "dateSubmitted": abstract.date_submitted.isoformat()
    }), 200


@app.route('/api/reviews', methods=['POST'])
def submit_review():
    """Submit a new review"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    rating = data.get("rating")
    comment = data.get("comment", "").strip()
    
    if not rating:
        return jsonify({"error": "Rating is required"}), 400
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Rating must be a valid number"}), 400
    
    # Validate comment length
    if comment and len(comment) > 1000:
        return jsonify({"error": "Comment must be less than 1000 characters"}), 400
    
    # Create review
    review = Reviews(
        rating=rating,
        comment=comment if comment else None,
        user_id=current_user.id if current_user.is_authenticated else None
    )
    
    try:
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            "message": "Thank you for your review",
            "review": review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to save review"}), 500

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Get all reviews with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    rating_filter = request.args.get('rating', type=int)
    
    # Limit per_page to prevent abuse
    per_page = min(per_page, 50)
    
    query = Reviews.query
    
    # Filter by rating if specified
    if rating_filter and 1 <= rating_filter <= 5:
        query = query.filter_by(rating=rating_filter)
    
    # Order by most recent first
    query = query.order_by(Reviews.created_at.desc())
    
    # Paginate
    reviews = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Calculate statistics
    total_reviews = Reviews.query.count()
    avg_rating = db.session.query(db.func.avg(Reviews.rating)).scalar()
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    
    # Rating distribution
    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = Reviews.query.filter_by(rating=i).count()
    
    return jsonify({
        "reviews": [review.to_dict() for review in reviews.items],
        "pagination": {
            "page": page,
            "pages": reviews.pages,
            "per_page": per_page,
            "total": reviews.total,
            "has_next": reviews.has_next,
            "has_prev": reviews.has_prev
        },
        "statistics": {
            "total_reviews": total_reviews,
            "average_rating": avg_rating,
            "rating_distribution": rating_counts
        }
    }), 200


@app.route('/api/reviews/stats', methods=['GET'])
def get_review_stats():
    """Get review statistics summary"""
    total_reviews = Reviews.query.count()
    
    if total_reviews == 0:
        return jsonify({
            "total_reviews": 0,
            "average_rating": 0,
            "rating_distribution": {str(i): 0 for i in range(1, 6)}
        }), 200
    
    avg_rating = db.session.query(db.func.avg(Reviews.rating)).scalar()
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    
    # Rating distribution
    rating_counts = {}
    for i in range(1, 6):
        count = Reviews.query.filter_by(rating=i).count()
        rating_counts[str(i)] = count
    
    return jsonify({
        "total_reviews": total_reviews,
        "average_rating": avg_rating,
        "rating_distribution": rating_counts
    }), 200


@app.route('/api/admin/reviews', methods=['GET'])
@admin_required
def admin_get_reviews():

    """Admin endpoint to get all reviews with user details"""

    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    
    reviews = Reviews.query.order_by(Reviews.created_at.desc()).all()
    
    reviews_data = []
    for review in reviews:
        review_data = review.to_dict()
        if review.user:
            review_data['user_email'] = review.user.email
            review_data['user_country'] = review.user.country
        reviews_data.append(review_data)
    
    return jsonify({
        "reviews": reviews_data,
        "total": len(reviews_data)
    }), 200
