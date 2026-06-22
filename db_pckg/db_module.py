from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine("sqlite:///bot_data.db", echo=False)  # echo=True для логов SQL
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    total_links = Column(Integer, default=0)


class SocialLink(Base):
    __tablename__ = "social_links"
    network_name = Column(String, primary_key=True)
    total_links = Column(Integer, default=0)


Base.metadata.create_all(engine)

default_networks = [
    "youtube",
    "twitter",
    "x",
    "instagram",
    "tiktok",
    "pinterest",
    "twitch",
    "reddit"
]

# Проверяем, есть ли уже записи
existing = session.query(SocialLink).count()
if existing == 0:
    for network in default_networks:
        session.add(SocialLink(network_name=network, total_links=0))
    session.commit()
    print("Соцсети предзаполнены.")
else:
    print("Соцсети уже есть, ничего не делаем.")


def add_social_link(network_name: str):
    social = session.query(SocialLink).filter_by(network_name=network_name).first()
    if social:
        social.total_links += 1
        session.commit()
    else:
        print(f"Сеть {network_name} не найдена в таблице.")


def add_user_link(user_id: int):
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        user.total_links += 1
    else:
        user = User(user_id=user_id, total_links=1)
        session.add(user)
    session.commit()


