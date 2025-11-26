from db.session import Base, get_session
from sqlalchemy import Column, Integer, String

# The User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

# The Helper Class
class UsersDB:
    def __init__(self):
        session = get_session()
        try:
            Base.metadata.create_all(bind=session.get_bind())
        finally:
            session.close()

    def register_user(self, name, username, email, password):
        session = get_session()
        try:
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                return False

            user = User(name=name, username=username, email=email, password=password)
            session.add(user)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error registering: {e}")
            return False
        finally:
            session.close()

    def authenticate_user(self, username, password):
        session = get_session()
        try:
            user = session.query(User).filter(
                User.username == username,
                User.password == password
            ).first()
            
            if not user:
                return None

            return {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "email": user.email,
            }
        finally:
            session.close()