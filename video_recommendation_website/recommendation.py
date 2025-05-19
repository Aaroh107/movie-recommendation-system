from app import db
from models import Video, Category, user_video_history
from sqlalchemy import func, desc, select
from collections import Counter
import random

def get_recommended_videos(user_id=None, limit=12):
    """
    Get recommended videos for a user or generic recommendations if no user_id
    
    Algorithm:
    1. If user_id is provided, get videos based on user's viewing history
       - Find most watched categories
       - Recommend videos from those categories that user hasn't watched
    2. If no user_id, return popular videos
    
    Args:
        user_id: The ID of the user to get recommendations for
        limit: Maximum number of videos to return
        
    Returns:
        List of Video objects
    """
    
    # If user_id is provided, get personalized recommendations
    if user_id:
        # Get videos the user has watched
        stmt = select(user_video_history).where(user_video_history.c.user_id == user_id)
        result = db.session.execute(stmt).fetchall()
        
        if result:
            # Get the video IDs the user has watched
            watched_video_ids = [row[1] for row in result]
            
            # Get the categories of videos the user has watched
            watched_videos = Video.query.filter(Video.id.in_(watched_video_ids)).all()
            watched_categories = [video.category_id for video in watched_videos]
            
            # Count category frequencies
            category_counts = Counter(watched_categories)
            top_categories = [cat_id for cat_id, _ in category_counts.most_common(3)]
            
            # Get recommendations from top categories that user hasn't watched yet
            recommendations = Video.query.filter(
                Video.category_id.in_(top_categories),
                ~Video.id.in_(watched_video_ids)
            ).order_by(desc(Video.view_count)).limit(limit).all()
            
            # If not enough recommendations, add popular videos from other categories
            if len(recommendations) < limit:
                more_videos = Video.query.filter(
                    ~Video.id.in_(watched_video_ids),
                    ~Video.id.in_([v.id for v in recommendations])
                ).order_by(desc(Video.view_count)).limit(limit - len(recommendations)).all()
                
                recommendations.extend(more_videos)
            
            return recommendations
    
    # Default: return popular videos
    return Video.query.order_by(desc(Video.view_count)).limit(limit).all()

def get_related_videos(video_id, limit=6):
    """
    Get videos related to the given video_id
    
    Algorithm:
    1. Get videos from the same category
    2. Exclude the current video
    3. Order by view count
    
    Args:
        video_id: The ID of the video to find related videos for
        limit: Maximum number of videos to return
        
    Returns:
        List of Video objects
    """
    # Get the video's category
    video = Video.query.get(video_id)
    if not video:
        return []
    
    # Get videos from the same category, excluding the current video
    related = Video.query.filter(
        Video.category_id == video.category_id,
        Video.id != video_id
    ).order_by(desc(Video.view_count)).limit(limit).all()
    
    # If not enough related videos, add some popular videos from other categories
    if len(related) < limit:
        more_videos = Video.query.filter(
            Video.category_id != video.category_id,
            Video.id != video_id
        ).order_by(desc(Video.view_count)).limit(limit - len(related)).all()
        
        related.extend(more_videos)
    
    return related

def update_video_history(user_id, video_id):
    """
    Update the user's video viewing history
    
    Args:
        user_id: The ID of the user
        video_id: The ID of the video being watched
    """
    # Check if entry already exists
    stmt = select(user_video_history).where(
        user_video_history.c.user_id == user_id,
        user_video_history.c.video_id == video_id
    )
    result = db.session.execute(stmt).fetchone()
    
    if not result:
        # Add new entry to history
        stmt = user_video_history.insert().values(
            user_id=user_id,
            video_id=video_id
        )
        db.session.execute(stmt)
        db.session.commit()
    else:
        # Update the watched_at timestamp
        stmt = user_video_history.update().where(
            user_video_history.c.user_id == user_id,
            user_video_history.c.video_id == video_id
        ).values(
            watched_at=func.current_timestamp()
        )
        db.session.execute(stmt)
        db.session.commit()
