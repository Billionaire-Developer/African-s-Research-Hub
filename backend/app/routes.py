from app import app, db
from datetime import datetime, timezone
from flask import request, jsonify, redirect
from flask_login import current_user, login_user, logout_user, login_required # type: ignore
from app.models import Users, Abstracts, Payments, Invoices, Contact, Notifications, Feedback, Reviews
from app.email_service import (
    send_abstract_confirmation_email, 
    send_payment_confirmation_email,
    send_abstract_review_email,
    send_admin_notification_email
)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/api/submit", methods=["POST"])
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
    author_id = data.get("author_id")

    if not all([title, content, field, institution, author_id]):
        return jsonify({"error": "Missing required fields"}), 400

    # Get the user to send confirmation email
    user = Users.query.get(author_id)
    if not user:
        return jsonify({"error": "Author not found"}), 404

    abstract = Abstracts(
        title = title,
        content = content,
        field = field,
        year = year,
        country = country,
        institution = institution,
        author_id = author_id
    )
    
    try:
        db.session.add(abstract)
        db.session.commit()
        
        # Send confirmation email to user
        send_abstract_confirmation_email(
            user_email=user.email,
            user_name=user.fullname,
            abstract_title=abstract.title,
            abstract_id=abstract.id
        )
        
        # Send notification email to admin
        send_admin_notification_email(
            abstract_title=abstract.title,
            author_name=user.fullname,
            abstract_id=abstract.id
        )
        
    except Exception as e:
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


@app.route("/api/abstracts/<int:id>", methods=["GET"])
def get_specific_abstract(id):
    abstract = Abstracts.query.get_or_404(id)
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
    method = data.get("method", "Bank")
    if not abstract_id:
        return jsonify({"error": "Missing abstract_id"}), 400

    # Check if abstract exists
    abstract = Abstracts.query.get(abstract_id)
    if not abstract:
        return jsonify({"error": "Abstract not found"}), 404

    # Generate invoice URL (dummy for now)
    invoice_url = f"http://example.com/invoice/{abstract_id}-{datetime.now(timezone.utc).timestamp()}"

    # Create Invoice (only use supported fields)
    invoice = Invoices(
        abstract_id = abstract_id, # type: ignore
        invoice_url = invoice_url, # type: ignore
    )
    try:
        db.session.add(invoice)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Create Payment (only use supported fields)
    payment = Payments(
        abstract_id = abstract_id, # type: ignore
        amount = amount, # type: ignore
        currency = currency, # type: ignore
        method = method #type: ignore
    )
    try:
        db.session.add(payment)
        db.session.commit()
    except Exception as e:
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
    user = Users.query.get(abstract.author_id) # type: ignore

    # Update payment status, date, and invoice paid status
    payment.status = "confirmed"
    payment.payment_date = datetime.now(timezone.utc)

    abstract_id = payment.abstract_id
    invoice = Invoices.query.filter_by(abstract_id=abstract_id).first()
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    invoice.paid = True

    try:
        db.session.commit()
        
        # Send payment confirmation email
        send_payment_confirmation_email(
            user_email=user.email, # type: ignore
            user_name=user.fullname, # type: ignore
            amount=payment.amount,
            currency=payment.currency,
            invoice_id=invoice.id
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Payment confirmed",
        "payment_id": payment.id,
        "status": payment.status,
        "payment_date": payment.payment_date.isoformat()
    }), 200


@app.route("/api/login", methods=["POST"])
@login_required
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
        return redirect("/api/admin")

    elif user.role in ["Student", "student"]:
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
        fullname = fullname, # type: ignore
        email = email, # type: ignore
        country = country, # type: ignore
        role = role # type: ignore
    )
    user.set_password(password) # type: ignore
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": f"Account created successfully, role: {user.role}"}), 201


@app.route("/api/contact", methods=["POST"])
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

    contact = Contact(
        name = name, # type: ignore
        email = email, # type: ignore
        message = message # type: ignore
    )

    try:
        db.session.add(contact)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # TODO: Add email notification logic here to notify admins

    return jsonify({"message": "Contact form submitted successfully", "id": contact.id}), 201


@app.route("/api/user/dashboard/<int:user_id>", methods=["GET"])
def user_dashboard(user_id):
    """Get student's dashboard info including their abstracts and payment status"""
    user = Users.query.get_or_404(user_id)

    # Get user's abstracts with related payment/invoice info
    user_abstracts = []
    for abstract in user.abstracts:
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
    notifications = Notifications.query.filter_by(user_id=user_id).order_by(Notifications.id.desc()).all()
    notification_data = [{
        "id": notif.id,
        "message": notif.message,
        "read": notif.read
    } for notif in notifications]

    dashboard_data = {
        "user": {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "country": user.country,
            "role": user.role
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
def review_abstract(abstract_id):
    """Admin endpoint to approve/reject abstract with feedback"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    action = data.get("action")  # "approve" or "reject"
    admin_id = data.get("admin_id")
    feedback_comment = data.get("feedback", "")

    if not all([action, admin_id]):
        return jsonify({"error": "Missing required fields: action and admin_id"}), 400

    if action not in ["approve", "reject"]:
        return jsonify({"error": "Action must be 'approve' or 'reject'"}), 400

    # Verify admin exists and has admin role
    admin = Users.query.get(admin_id)
    if not admin or admin.role != "admin":
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    abstract = Abstracts.query.get_or_404(abstract_id)
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
            user_email=user.email, # type: ignore
            user_name=user.fullname, # type: ignore
            abstract_title=abstract.title,
            status=abstract.status,
            feedback=feedback_comment if feedback_comment else None
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": f"Abstract {action}d successfully",
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

    abstract = Abstracts.query.get_or_404(abstract_id)

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

@app.route('/api/review', methods=['POST'])
def review():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    rating = data.get("rating")
    comment = data.get("comment")
    
    if not rating:
        return jsonify({"error": "Missing required data"}), 400
    
    review = Reviews(
        rating=rating,
        comment=comment
    )
    
    try:
        db.session.add(review)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Thank you for your review"})