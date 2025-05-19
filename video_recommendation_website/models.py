import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

# Association table for user video history
user_video_history = db.Table('user_video_history',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('video_id', db.Integer, db.ForeignKey('video.id'), primary_key=True),
    db.Column('watched_at', db.DateTime, default=datetime.datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='user', lazy=True)
    viewed_videos = db.relationship('Video', secondary=user_video_history, 
                                    lazy='subquery', backref=db.backref('viewers', lazy=True))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    videos = db.relationship('Video', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500), nullable=False)  # URL to the video source
    thumbnail = db.Column(db.String(500))  # URL to the thumbnail image
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='video', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Video {self.title}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.user.username}>'

def seed_initial_data():
    """Seed the database with initial data if tables are empty"""
    if User.query.count() == 0 and Category.query.count() == 0:
        # Create demo user
        demo_user = User(
            username="demo_user",
            email="demo@example.com"
        )
        demo_user.set_password("password")  # In production, use strong passwords
        db.session.add(demo_user)
        
        # Create categories
        categories = [
            {"name": "Music", "description": "Music videos, performances and more"},
            {"name": "Tech", "description": "Technology tutorials and reviews"},
            {"name": "Gaming", "description": "Gaming content and walkthroughs"},
            {"name": "Science", "description": "Educational science content"},
            {"name": "Cooking", "description": "Recipes and cooking tutorials"}
        ]
        
        for cat_data in categories:
            category = Category(**cat_data)
            db.session.add(category)
        
        db.session.commit()  # Commit to get category IDs
        
        # Get categories for reference
        music = Category.query.filter_by(name="Music").first()
        tech = Category.query.filter_by(name="Tech").first()
        gaming = Category.query.filter_by(name="Gaming").first()
        science = Category.query.filter_by(name="Science").first()
        cooking = Category.query.filter_by(name="Cooking").first()
        
        # Create demo videos with publicly accessible videos
        videos = [
            {
                "title": "Amazing Guitar Solo",
                "description": "Watch this incredible guitar performance that will blow your mind.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "thumbnail": "https://dummyimage.com/320x180/3273dc/ffffff.png&text=Amazing+Guitar+Solo",
                "category_id": music.id
            },
            {
                "title": "Learn Python in 10 Minutes",
                "description": "A quick overview of Python programming basics.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                "thumbnail": "https://dummyimage.com/320x180/209cee/ffffff.png&text=Learn+Python",
                "category_id": tech.id
            },
            {
                "title": "Minecraft Advanced Building Techniques",
                "description": "Learn how to create amazing structures in Minecraft.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                "thumbnail": "https://dummyimage.com/320x180/ff3860/ffffff.png&text=Minecraft+Building",
                "category_id": gaming.id
            },
            {
                "title": "How Black Holes Work",
                "description": "An educational video about the physics of black holes.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                "thumbnail": "https://dummyimage.com/320x180/ffdd57/000000.png&text=Black+Holes",
                "category_id": science.id
            },
            {
                "title": "Perfect Chocolate Cake Recipe",
                "description": "Learn how to bake the perfect chocolate cake from scratch.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
                "thumbnail": "https://dummyimage.com/320x180/23d160/ffffff.png&text=Chocolate+Cake",
                "category_id": cooking.id
            },
            {
                "title": "Piano Basics for Beginners",
                "description": "Start learning piano with these simple lessons.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
                "thumbnail": "https://dummyimage.com/320x180/3273dc/ffffff.png&text=Piano+Basics",
                "category_id": music.id
            },
            {
                "title": "Web Development in 2023",
                "description": "The latest trends and technologies in web development.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
                "thumbnail": "https://dummyimage.com/320x180/209cee/ffffff.png&text=Web+Development",
                "category_id": tech.id
            },
            {
                "title": "Advanced JavaScript Techniques",
                "description": "Master advanced JavaScript concepts and patterns.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
                "thumbnail": "https://dummyimage.com/320x180/209cee/ffffff.png&text=Advanced+JavaScript",
                "category_id": tech.id
            },
            {
                "title": "The Legend of Zelda Walkthrough",
                "description": "Complete walkthrough for the latest Legend of Zelda game.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
                "thumbnail": "https://dummyimage.com/320x180/ff3860/ffffff.png&text=Zelda+Walkthrough",
                "category_id": gaming.id
            },
            {
                "title": "Understanding DNA",
                "description": "An in-depth look at the structure and function of DNA.",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
                "thumbnail": "https://dummyimage.com/320x180/ffdd57/000000.png&text=DNA+Science",
                "category_id": science.id
            }
        ]
        
        # Add videos to database
        for video_data in videos:
            video = Video(**video_data)
            db.session.add(video)
        
        db.session.commit()  # Commit to get video IDs
        
        # Add some comments
        videos = Video.query.all()
        user = User.query.first()
        
        for video in videos[:5]:  # Add comments to the first 5 videos
            comment = Comment(
                content="This is an awesome video! Thanks for sharing.",
                user_id=user.id,
                video_id=video.id
            )
            db.session.add(comment)
        
        db.session.commit()
