from sqlalchemy import select, and_, not_, func, desc, exists
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User, Like

async def get_next_profile(session: AsyncSession, current_user: User, 
                           target_gender: str = None, 
                           min_age: int = None, 
                           max_age: int = None):
    """
    Finds the next profile for the current user with dynamic filters.
    Optimized for large datasets.
    """
    import logging
    from sqlalchemy.orm import aliased
    
    # Use provided filters or fallback to user defaults
    gender_filter = (target_gender or current_user.target_gender or "").strip().lower()
    
    logging.info(f"MATCHING DB CHECK: user={current_user.id}, target_gender={gender_filter}")

    # Explicit alias to avoid correlation ambiguity
    seen_user = aliased(User)
    seen_stmt = exists().where(
        and_(
            Like.user_id == current_user.id,
            Like.target_id == User.id
        )
    )
    
    conditions = [
        User.id != current_user.id,
        User.gender == gender_filter,
        User.is_banned == False,
        User.is_frozen == False,
        ~seen_stmt
    ]
    
    if min_age:
        conditions.append(User.age >= min_age)
    if max_age:
        conditions.append(User.age <= max_age)
    
    # Distance in KM - Handle cases where location might be missing
    if current_user.location is not None:
        distance_expr = func.ST_Distance(User.location, current_user.location) / 1000
    else:
        distance_expr = func.cast(0, func.Float)
    
    query = (
        select(User, distance_expr.label("distance"))
        .where(and_(*conditions))
        .order_by(
            desc(User.boost_points > 0),
            distance_expr
        )
        .limit(1)
    )
    
    try:
        # Debug: check total users count and gender counts
        # This is for development debugging only
        total_q = select(func.count(User.id))
        total_res = await session.execute(total_q)
        logging.info(f"TOTAL USERS IN DB: {total_res.scalar()}")
        
        gender_q = select(User.gender, func.count(User.id)).group_by(User.gender)
        gender_res = await session.execute(gender_q)
        logging.info(f"GENDER STATS: {gender_res.all()}")

        result = await session.execute(query)
        row = result.first()
        if row:
            user, distance = row
            logging.info(f"Found profile! ID: {user.id}, Gender: {user.gender}")
            if user.boost_points > 0:
                user.boost_points -= 1
                await session.flush()
            return user, distance
        else:
            logging.info(f"NO PROFILES FOUND for conditions: gender={gender_filter}, range={min_age}-{max_age}")
    except Exception as e:
        logging.error(f"DATABASE QUERY ERROR in get_next_profile: {e}")
        
    return None, None

async def handle_interaction(session: AsyncSession, user_id: int, target_id: int, is_like: bool):
    """
    Handles a Like/Dislike action.
    Returns: bool (True if mutual match)
    """
    # 1. Save the interaction
    new_like = Like(user_id=user_id, target_id=target_id, is_like=is_like)
    session.add(new_like)
    
    # 2. Check for mutual match if it's a 'Like'
    is_match = False
    if is_like:
        check_mutual = select(Like).where(
            and_(
                Like.user_id == target_id,
                Like.target_id == user_id,
                Like.is_like == True
            )
        )
        mutual_result = await session.execute(check_mutual)
        mutual_like = mutual_result.scalar_one_or_none()
        
        if mutual_like:
            is_match = True
            new_like.is_match = True
            mutual_like.is_match = True
            
    await session.commit()
    return is_match
