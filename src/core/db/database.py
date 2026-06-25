from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

class Base(DeclarativeBase):

    def create_db_engine(db_path: str = "quizbot.db"):

        # создаем движок, который может подключаться к БД

        return create_engine(f"sqlite:///{db_path}")

    def init_db(engine) -> None:

        # создаем таблицы

        Base.metadata.create_all(engine)

    def create_session_factory(engine) -> sessionmaker[Session]:

        # создаем фабрику сессий, которая умеет создавать подключения к БД

        return sessionmaker(bind=engine)



