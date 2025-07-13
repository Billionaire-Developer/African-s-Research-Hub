from app import app, db
from flask import request, jsonify
from datetime import datetime, timedelta, timezone
from app.models import Users, Abstracts, Payments, Invoices


@app.route("/api/submit", methods=["POST"])
def submit_abstract():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    title = data.get("title")
    content = data.get("content")
    field = data.get("field")
    institution = data.get("institution")
    author_id = data.get("author_id")

    if not all([title, content, field, institution, author_id]):
        return jsonify({"error": "Missing required fields"}), 400

    abstract = Abstracts(
        title=title, # type: ignore
        content=content, # type: ignore
        field=field, # type: ignore
        institution=institution, # type: ignore
        author_id=author_id # type: ignore
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
    "yearOfResearch": abstract.year_of_research,
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
        "yearOfResearch": abstract.year_of_research,
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
    invoice_url = f"https://example.com/invoice/{abstract_id}-{datetime.now(timezone.utc).timestamp()}"
    generated_date = datetime.now(timezone.utc)
    due_date = generated_date + timedelta(weeks=2)

    # Create Invoice (only use supported fields)
    invoice = Invoices(
        abstract_id = abstract_id, # type: ignore
        invoice_url = invoice_url # type: ignore
    )
    try:
        db.session.add(invoice)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Create Payment (only use supported fields)
    payment = Payments(
        abstract_id=abstract_id, # type: ignore
        amount=amount, # type: ignore
        currency=currency # type: ignore
    )
    db.session.add(payment)
    db.session.commit()

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

    # Update payment status and date
    payment.status = "confirmed"
    payment.payment_date = datetime.now(timezone.utc)
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
    
    user = Users(
        email = email, # type: ignore
        password = password # type: ignore
    )
    
    if user.query.filter_by(email=email).first() is None:
        return jsonify({"error": "Email not found"}), 401
    
    elif user.verify_password(password) == False:
        return jsonify({"error": "Invalid password"}), 401
    
    elif user.query.filter_by(email=email).first() is None and user.verify_password(password) != True:
        return jsonify({"error": "Invalid email and password"}), 401
    
    else:
        return jsonify({"message": "You have been successfully logged in"})
    

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
        password = password, # type: ignore
        role = role # type: ignore
    )
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Account created successfully, role: user.role}"}), 201

# ----- Remaining routes -----
# 
# GET /api/user/dashboard Get student's dashboard info
# POST /api/admin/review/:id Approve/reject abstract
# POST /api/resubmit/:id Allow students to update rejected abstract
# POST /api/contact