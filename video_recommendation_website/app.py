import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Use in-memory SQLite for demonstration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Import models and recommendation engine
from models import Video, Category, Comment, User, user_video_history
from recommendation import get_recommended_videos, get_related_videos, update_video_history

with app.app_context():
    # Create tables
    db.create_all()
    
    # Import seed data function and populate database if empty
    from models import seed_initial_data
    seed_initial_data()

# Routes
@app.route('/')
def index():
    recommended_videos = get_recommended_videos(session.get('user_id'))
    categories = Category.query.all()
    return render_template('index.html', 
                           recommended_videos=recommended_videos,
                           categories=categories,
                           title="Home - Video Recommendations")

@app.route('/video/<int:video_id>')
def video_detail(video_id):
    try:
        video = Video.query.get_or_404(video_id)
        related_videos = get_related_videos(video_id)
        comments = Comment.query.filter_by(video_id=video_id).order_by(Comment.created_at.desc()).all()
        
        # Update view count
        video.view_count += 1
        db.session.commit()
        
        # Record this view in user history if user is identified
        if 'user_id' in session:
            update_video_history(session['user_id'], video_id)
        
        # Log the successful video load
        logger.debug(f"Video {video_id} loaded successfully, current view count: {video.view_count}")
        
        return render_template('video.html', 
                              video=video, 
                              related_videos=related_videos,
                              comments=comments,
                              title=f"{video.title} - Video Recommendations")
    except Exception as e:
        logger.error(f"Error loading video {video_id}: {str(e)}")
        raise

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    videos = Video.query.filter_by(category_id=category_id).order_by(Video.view_count.desc()).all()
    return render_template('category.html', 
                          category=category, 
                          videos=videos,
                          title=f"{category.name} - Video Recommendations")

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    videos = Video.query.filter(Video.title.ilike(f'%{query}%') | 
                               Video.description.ilike(f'%{query}%')).all()
    return render_template('search.html', 
                          query=query, 
                          videos=videos,
                          title=f"Search Results for '{query}' - Video Recommendations")

# API endpoints
@app.route('/api/videos')
def api_videos():
    videos = Video.query.all()
    return jsonify([{
        'id': v.id,
        'title': v.title,
        'thumbnail': v.thumbnail,
        'view_count': v.view_count,
        'category': v.category.name
    } for v in videos])

@app.route('/api/videos/<int:video_id>')
def api_video_detail(video_id):
    video = Video.query.get_or_404(video_id)
    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'url': video.url,
        'thumbnail': video.thumbnail,
        'view_count': video.view_count,
        'category': video.category.name,
        'created_at': video.created_at.isoformat()
    })

@app.route('/api/videos/<int:video_id>/comments', methods=['GET'])
def api_video_comments(video_id):
    comments = Comment.query.filter_by(video_id=video_id).order_by(Comment.created_at.desc()).all()
    return jsonify([{
        'id': c.id,
        'content': c.content,
        'user': c.user.username,
        'created_at': c.created_at.isoformat()
    } for c in comments])

@app.route('/api/videos/<int:video_id>/comments', methods=['POST'])
def api_add_comment(video_id):
    # For simplicity, we're using a demo user
    if 'user_id' not in session:
        session['user_id'] = 1  # Demo user ID
    
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Comment content is required'}), 400
    
    new_comment = Comment(
        content=content,
        video_id=video_id,
        user_id=session['user_id']
    )
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        'id': new_comment.id,
        'content': new_comment.content,
        'user': new_comment.user.username,
        'created_at': new_comment.created_at.isoformat()
    }), 201

@app.route('/api/recommended')
def api_recommended():
    user_id = session.get('user_id')
    videos = get_recommended_videos(user_id)
    return jsonify([{
        'id': v.id,
        'title': v.title,
        'thumbnail': v.thumbnail,
        'view_count': v.view_count,
        'category': v.category.name
    } for v in videos])

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Page Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', title="Server Error"), 500
