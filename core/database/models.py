from datetime import datetime
from sqlalchemy import BigInteger, Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, relationship
from geoalchemy2 import Geometry

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram User ID
    name = Column(String(100), nullable=False)
    nickname = Column(String(100), nullable=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False, index=True)  # Added index
    target_gender = Column(String(10), nullable=False, index=True) # Added index
    target_min_age = Column(Integer, default=14)
    target_max_age = Column(Integer, default=100)
    photo_id = Column(String(255), nullable=True) # For Telegram display
    photo_path = Column(String(255), nullable=True) # For local archive
    language = Column(String(2), default='uz')  # 'uz', 'ru', 'tg'
    phone_number = Column(String(20), nullable=True)
    
    # PostGIS Geometry type for location (Point, SRID 4326)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    
    boost_points = Column(Integer, default=0, index=True) # Added index
    referred_by = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    is_banned = Column(Boolean, default=False, index=True)
    
    pending_likes_count = Column(Integer, default=0)
    last_like_notification_id = Column(BigInteger, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    likes_sent = relationship("Like", foreign_keys="Like.user_id", back_populates="user")
    likes_received = relationship("Like", foreign_keys="Like.target_id", back_populates="target")
    reports_sent = relationship("Report", foreign_keys="Report.reporter_id", back_populates="reporter")
    reports_received = relationship("Report", foreign_keys="Report.target_id", back_populates="target")

class Like(Base):
    # ... (existing Like model code)
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    target_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    is_like = Column(Boolean, nullable=False, index=True)  # True = Like, False = Dislike
    is_match = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="likes_sent")
    target = relationship("User", foreign_keys=[target_id], back_populates="likes_received")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reporter_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    target_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports_sent")
    target = relationship("User", foreign_keys=[target_id], back_populates="reports_received")
