"""
Initialize database with default data
"""
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import User, ResearchGroup
from app.services.auth import get_password_hash
from app.config import get_settings

settings = get_settings()

def init_db():
    """Initialize database tables and default data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create default lab group
        lab_group = db.query(ResearchGroup).filter(
            ResearchGroup.name == settings.LAB_NAME
        ).first()
        
        if not lab_group:
            lab_group = ResearchGroup(
                name=settings.LAB_NAME,
                description=f"Default {settings.LAB_NAME} group for all members"
            )
            db.add(lab_group)
            db.commit()
            db.refresh(lab_group)
            print(f"✓ Created default lab group: {settings.LAB_NAME}")
        
        # Create default admin user
        admin_user = db.query(User).filter(User.is_admin == True).first()
        
        if not admin_user:
            admin_user = User(
                name="Admin User",
                email=settings.FIRST_SUPERUSER,
                password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_admin=True,
                email_notifications=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✓ Created admin user: {settings.FIRST_SUPERUSER}")
            print(f"  Password: {settings.FIRST_SUPERUSER_PASSWORD}")
        
        print("✓ Database initialized successfully")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
