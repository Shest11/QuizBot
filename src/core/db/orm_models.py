import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

class SurveyModel(Base):

    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    start_question_id: Mapped[int] = mapped_column(Integer)


class QuestionModel(Base):

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.id"), index=True)
    text: Mapped[str] = mapped_column(String)
    question_type: Mapped[str] = mapped_column(String)  # "choice" или "free_text"
    next_question_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AnswerModel(Base):

    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    text: Mapped[str] = mapped_column(String)
    next_question_id: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer, default=0)


class QuizSession(Base):

    __tablename__ = "quiz_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.id"), index=True)
    current_question_id: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer, default=0)


class QuizResult(Base):

    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.id"), index=True)
    total_score: Mapped[int] = mapped_column(Integer)
    result_text: Mapped[str] = mapped_column(String)
    finished_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now(datetime.UTC))


