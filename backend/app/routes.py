from app import app, db
from flask import request, jsonify
from datetime import datetime, timezone, timedelta
from app.models import Users, Abstracts, Payments, Invoices, Contact


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

    abstract = Abstracts(
        title = title, # type: ignore
        content = content, # type: ignore
        field = field, # type: ignore
        year = year, # type: ignore
        country = country, # type: ignore
        institution = institution, # type: ignore
        author_id = author_id # type: ignore
    )
    try:
        db.session.add(abstract)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Add email notification logic here

    return jsonify({"message": "Abstract submitted successfully", "id": abstract.id}), 201


@app.route("/api/abstracts", methods=["GET"])
def get_abstracts():
    abstracts = Abstracts.query.all()
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


@app.route("/api/payments/initiate", methods=["POST"])
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

    # Update payment status,date, and invoice paid status
    payment.status = "confirmed"
    payment.payment_date = datetime.now(timezone.utc)

    abstract_id = payment.abstract_id
    invoice = Invoices.query.filter_by(abstract_id=abstract_id).first()
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404
    
    invoice.paid = not invoice.paid
    
    try:
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Payment confirmed",
        "payment_id": payment.id,
        "status": payment.status,
        "payment_date": payment.payment_date.isoformat()
    }), 200


@app.route("/api/login", methods=["POST"])
def login():
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
    
    return jsonify({"message": "You have been successfully logged in"}), 201
    

@app.route("/api/register", methods=["POST"])
def register():
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
    
    return jsonify({
        "message": "Contact form submitted successfully",
        "id": contact.id
    }), 201

# ----- Remaining routes -----
# 
# GET /api/user/dashboard Get student's dashboard info
# POST /api/admin/review/:id Approve/reject abstract
# POST /api/resubmit/:id Allow students to update rejected abstract