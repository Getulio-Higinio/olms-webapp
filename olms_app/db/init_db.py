from olms_app.db.database import Base, engine, get_session
from olms_app.db import models
from olms_app.db.models import User
from olms_app.auth.login import hash_password


def init_db():
    Base.metadata.create_all(bind=engine)

    session = get_session()

    admin = session.query(User).filter(User.username == "admin").first()

    if not admin:
        admin = User(
            username="admin",
            full_name="System Administrator",
            password_hash=hash_password("admin123"),
            role="ADMIN",
            is_active=1,
        )
        session.add(admin)
        session.commit()

    session.close()
