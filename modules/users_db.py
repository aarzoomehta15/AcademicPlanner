from db.session import Base, get_session
from sqlalchemy import Column, Integer, String


class UsersDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    def __init__(self):
        Base.metadata.create_all(bind=get_session().get_bind())

    # REGISTER USER
    def register_user(self, name, username, email, password):
        session = get_session()
        existing = session.query(UsersDB).filter(UsersDB.username == username).first()
        if existing:
            return False

        user = UsersDB()
        user.name = name
        user.username = username
        user.email = email
        user.password = password
        session.add(user)
        session.commit()
        return True

    # LOGIN / AUTHENTICATE USER
    def authenticate_user(self, username, password):
        session = get_session()
        user = session.query(UsersDB).filter(
            UsersDB.username == username,
            UsersDB.password == password
        ).first()
        if not user:
            return None

        return {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
        }
