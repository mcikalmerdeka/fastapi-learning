"""
Post Routes
Handles all post-related operations: CRUD, likes, retweets, and feed queries
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func  # SQL aggregate functions (COUNT, etc.)
from typing import List, Annotated
from datetime import timedelta, datetime, timezone

from .. import models, schemas, auth
from ..database import get_db
from .. import exceptions  # Import from parent package

# Setup Router with /posts prefix
router = APIRouter(
    prefix="/posts",  # All routes start with /posts
    tags=["posts"],   # Groups in API docs
)

# Type alias for dependency injection
db_dependency = Annotated[Session, Depends(get_db)]

# ============ Get Posts Endpoint ============
# GET /posts/ - Retrieve a list of posts (paginated)
@router.get("/", response_model=List[schemas.Post])
def read_posts(db: db_dependency, skip: int = 0, limit: int = 10):
    """
    Get posts with pagination
    
    Query parameters:
    - skip: How many posts to skip (for pagination, default 0)
    - limit: Max number of posts to return (default 10)
    
    Returns posts ordered by most recent first
    """
    # Query posts, order by newest first, apply pagination
    # offset(skip): skip N records (e.g., skip=10 for page 2)
    # limit(limit): return max N records
    posts = db.query(models.Post).order_by(models.Post.timestamp.desc()).offset(skip).limit(limit).all()
    return posts

# ============ Create New Post Endpoint ============
# POST /posts/ - Create a new post
@router.post("/", response_model=schemas.Post)
def create_new_post(
    post: schemas.PostCreate,  # Request body containing post content
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),  # Requires authentication
):
    """
    Create a new post
    
    Requires authentication - the authenticated user becomes the post owner
    
    Request body: {"content": "Your post text here"}
    """
    # Create new Post object, linking it to the current user
    db_post = models.Post(content=post.content, owner_id=current_user.id)
    
    # Add to database session
    db.add(db_post)
    
    # Commit to save the post
    db.commit()
    
    # Refresh to get auto-generated fields (id, timestamp)
    db.refresh(db_post)
    
    # Return the created post
    return db_post

# ============ Delete Post Endpoint ============
# DELETE /posts/{post_id} - Delete a post
@router.delete("/{post_id}", status_code=204)
def delete_existing_post(
    post_id: int,  # Post ID from URL path
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),  # Must be authenticated
):
    """
    Delete a post
    
    Only the post owner can delete their own posts
    
    Authorization check: ensures current_user owns the post
    """
    # Find the post by ID
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    # Check if post exists AND belongs to current user
    # Security: users can only delete their own posts
    if post is None or post.owner_id != current_user.id:
        exceptions.raise_not_found_exception('Post not found')
    
    # Delete the post
    db.delete(post)
    
    # Commit the deletion
    db.commit()
    
    # 204 No Content - successful deletion
    return

# ============ Update Post Endpoint ============
# PUT /posts/{post_id} - Edit a post (with time restriction)
@router.put("/{post_id}", response_model=schemas.Post)
def update_post(
    post_id: int,  # Post ID from URL
    post_update: schemas.PostUpdate,  # New content in request body
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Update a post's content
    
    Business rules:
    - Only post owner can edit
    - Can only edit within 10 minutes of creation (like Twitter)
    
    This demonstrates time-based authorization logic
    """
    # Find the post
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        exceptions.raise_not_found_exception('Post not found')
    
    # Authorization: only the owner can edit
    if post.owner_id != current_user.id:
        exceptions.raise_forbidden_exception('Not authorized to edit this post')

    # Time-based restriction: can only edit within 10 minutes
    # Ensure timestamp is timezone-aware for comparison
    post_timestamp_aware = post.timestamp.replace(tzinfo=timezone.utc)
    time_since_creation = datetime.now(timezone.utc) - post_timestamp_aware
    
    if time_since_creation > timedelta(minutes=10):
        exceptions.raise_not_found_exception("You can only edit a post within 10 minutes of its creation")
    
    # Update the content
    post.content = post_update.content
    
    # Mark as modified in session
    db.add(post)
    
    # Save changes
    db.commit()
    
    # Return updated post
    return post

# ============ Like Post Endpoint ============
# POST /posts/{post_id}/like - Like a post
@router.post("/{post_id}/like", status_code=204)
def like_post(
    post_id: int,  # Post ID from URL
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Like a post
    
    - Creates a Like record linking user to post
    - Prevents duplicate likes (composite primary key enforces this at DB level)
    """
    # Verify post exists
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        exceptions.raise_not_found_exception('Post not found')
    
    # Check if user already liked this post
    # filter_by() is shorthand for filter() with exact matches
    like = db.query(models.Like).filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        exceptions.raise_not_found_exception("Already liked")
    
    # Create new Like record
    new_like = models.Like(user_id=current_user.id, post_id=post_id)
    
    # Save to database
    db.add(new_like)
    db.commit()
    
    # 204 No Content - success
    return

# ============ Unlike Post Endpoint ============
# POST /posts/{post_id}/unlike - Remove a like
@router.post("/{post_id}/unlike", status_code=204)
def unlike_post(
    post_id: int,
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Unlike a post (remove like)
    
    Deletes the Like record if it exists
    """
    # Find the like record
    like = db.query(models.Like).filter_by(user_id=current_user.id, post_id=post_id).first()
    if not like:
        exceptions.raise_not_found_exception("Not liked yet")
    
    # Delete the like
    db.delete(like)
    db.commit()
    
    return

# ============ Retweet Post Endpoint ============
# POST /posts/{post_id}/retweet - Retweet a post
@router.post("/{post_id}/retweet", status_code=204)
def retweet_post(
    post_id: int,
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Retweet a post
    
    Similar to like but creates a Retweet record (includes timestamp)
    """
    # Verify post exists
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        exceptions.raise_not_found_exception('Post not found')
    
    # Check if already retweeted
    retweet = db.query(models.Retweet).filter_by(user_id=current_user.id, post_id=post_id).first()
    if retweet:
        exceptions.raise_not_found_exception("Already retweeted")
    
    # Create Retweet record (includes timestamp unlike Like)
    new_retweet = models.Retweet(user_id=current_user.id, post_id=post_id)
    db.add(new_retweet)
    db.commit()
    
    return

# ============ Unretweet Post Endpoint ============
# POST /posts/{post_id}/unretweet - Remove a retweet
@router.post("/{post_id}/unretweet", status_code=204)
def unretweet_post(
    post_id: int,
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Remove a retweet
    """
    # Find the retweet record
    retweet = db.query(models.Retweet).filter_by(user_id=current_user.id, post_id=post_id).first()
    if not retweet:
        exceptions.raise_not_found_exception("Not retweeted yet")
    
    # Delete the retweet
    db.delete(retweet)
    db.commit()
    
    return

# ============ Get Posts with Engagement Counts Endpoint ============
# GET /posts/with_counts/ - Get posts with likes/retweets counts
@router.get("/with_counts/", response_model=List[schemas.PostWithCounts])
def read_posts_with_counts(db: db_dependency):
    """
    Advanced endpoint: Get posts with aggregated engagement metrics
    
    This demonstrates:
    - SQL subqueries for aggregation
    - Multiple table joins
    - Using func.count() for counting related records
    - Using func.coalesce() to handle NULL values (posts with 0 likes/retweets)
    
    This is more efficient than fetching posts and counting likes/retweets separately
    """
    
    # STEP 1: Create a subquery to count likes per post
    # This is like a temporary table with columns: post_id, likes_count
    likes_subq = (
        db.query(
            models.Like.post_id,  # Group by post
            func.count(models.Like.user_id).label('likes_count')  # Count likes
        )
        .group_by(models.Like.post_id)  # One row per post
        .subquery()  # Make it a subquery to join later
    )

    # STEP 2: Create a subquery to count retweets per post
    # Similar to likes_subq, creates: post_id, retweets_count
    retweets_subq = (
        db.query(
            models.Retweet.post_id,
            func.count(models.Retweet.user_id).label('retweets_count')
        )
        .group_by(models.Retweet.post_id)
        .subquery()
    )

    # STEP 3: Main query - join everything together
    # This creates a result with: Post object, username, likes_count, retweets_count
    posts = (
        db.query(
            models.Post,  # Get all post columns
            models.User.username.label('owner_username'),  # Get owner's username
            # coalesce returns first non-NULL value (defaults to 0 if post has no likes)
            func.coalesce(likes_subq.c.likes_count, 0).label('likes_count'),
            func.coalesce(retweets_subq.c.retweets_count, 0).label('retweets_count')
        )
        # INNER JOIN User - every post must have an owner
        .join(models.User, models.Post.owner_id == models.User.id)
        
        # LEFT OUTER JOIN likes subquery - includes posts even if they have 0 likes
        .outerjoin(likes_subq, models.Post.id == likes_subq.c.post_id)
        
        # LEFT OUTER JOIN retweets subquery - includes posts even if they have 0 retweets
        .outerjoin(retweets_subq, models.Post.id == retweets_subq.c.post_id)
        
        .order_by(models.Post.timestamp.desc())  # Newest first
        .all()  # Execute and return all results
    )

    # STEP 4: Transform database results into Pydantic schema objects
    # The query returns tuples of (Post, username, likes_count, retweets_count)
    response_posts = []
    for post, owner_username, likes_count, retweets_count in posts:
        # Create PostWithCounts schema object for each post
        response_posts.append(schemas.PostWithCounts(
            id=post.id,
            content=post.content,
            timestamp=post.timestamp,
            owner_id=post.owner_id,
            owner_username=owner_username,  # From the join
            likes_count=likes_count,  # From the subquery
            retweets_count=retweets_count  # From the subquery
        ))

    return response_posts


