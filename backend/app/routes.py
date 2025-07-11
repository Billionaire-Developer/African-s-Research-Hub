from app import app, db
from app.models import Users, Abstracts
from flask import request, jsonify, render_template


@app.route('/api/submit', methods=['POST'])
def submit_abstract():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    title = data.get('title')
    content = data.get('content')
    field = data.get('field')
    institution = data.get('institution')
    author_id = data.get('author_id')

    if not all([title, content, field, institution, author_id]):
        return jsonify({'error': 'Missing required fields'}), 400

    abstract = Abstracts(
        title=title, # type: ignore
        content=content, # type: ignore
        field=field, # type: ignore
        institution=institution, # type: ignore
        author_id=author_id # type: ignore
    )
    db.session.add(abstract)
    db.session.commit()
    
    # Add email notification logic here

    return jsonify({'message': 'Abstract submitted successfully', 'id': abstract.id}), 201

@app.route('/api/abstracts', methods=['GET'])
def get_abstracts():
    abstracts = Abstracts.query.all()
    return jsonify([{
        'id': abstract.id,
        'title': abstract.title,
        'content': abstract.content,
        'field': abstract.field,
        'institution': abstract.institution,
        'year_of_research': abstract.year_of_research,
        'keywords': abstract.keywords,
        'status': abstract.status,
        'author_id': abstract.author_id,
        'date_submitted': abstract.date_submitted.isoformat()
    } for abstract in abstracts]), 200
    
@app.route('/api/abstracts/<int:id>', methods=['GET'])
def get_abstract(id):
    abstract = Abstracts.query.get_or_404(id)
    return jsonify({
        'id': abstract.id,
        'title': abstract.title,
        'content': abstract.content,
        'field': abstract.field,
        'institution': abstract.institution,
        'year_of_research': abstract.year_of_research,
        'keywords': abstract.keywords,
        'status': abstract.status,
        'author_id': abstract.author_id,
        'date_submitted': abstract.date_submitted.isoformat()
    }), 200
    
