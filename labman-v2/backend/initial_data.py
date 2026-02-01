import logging
import sys
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.config import get_settings
from app.utils.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    settings = get_settings()
    
    # Create tables
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
        if not user:
            logger.info("Creating first superuser...")
            user = User(
                email=settings.FIRST_SUPERUSER,
                password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                name="Admin User",
                is_admin=True,
                email_notifications=True
            )
            db.add(user)
            db.commit()
            logger.info("First superuser created")
        else:
            logger.info("First superuser already exists")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")
