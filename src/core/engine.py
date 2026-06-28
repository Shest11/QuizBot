from sqlalchemy.orm import Session, sessionmaker

from core.db.orm_models import QuizSession
from core.models import Question
from core.repository import build_survey, list_surveys

class SurveyEngine:

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_available_surveys(self):
        with self._session_factory() as db_session:
            return list_surveys(db_session)

    def start_survey(self, user_id: int, survey_id: int) -> Question:
        with self._session_factory() as db_session:
            survey = build_survey(db_session, survey_id)

            existing = db_session.query(QuizSession).filter_by(
                user_id=user_id, survey_id=survey_id
            ).one_or_none()
            if existing is not None:
                db_session.delete(existing)

            new_session = QuizSession(
                user_id=user_id,
                survey_id=survey_id,
                current_question_id=survey.start_question_id,
                score=0,
            )
            db_session.add(new_session)
            db_session.commit()

            return survey.get_question(survey.start_question_id)