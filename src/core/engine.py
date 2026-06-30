from sqlalchemy.orm import Session, sessionmaker

from core.db.orm_models import QuizResult, QuizSession
from core.models import Question
from core.repository import SurveyRepository

END_OF_SURVEY = 0

def find_next_step(question: Question, answer_text: str) -> tuple[int, int]:

    if question.question_type == "free_text":
        return question.next_question_id, 0

    for answer in question.answers:
        if answer.text == answer_text:
            return answer.next_question_id, answer.score


class SurveyEngine:

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._repository = SurveyRepository()

    def list_available_surveys(self):
        with self._session_factory() as db_session:
            return self._repository.list_surveys(db_session)

    def start_survey(self, user_id: int, survey_id: int) -> Question:
        with self._session_factory() as db_session:
            survey = self._repository.get_survey(db_session, survey_id)

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

    def answer(self, user_id: int, survey_id: int, answer_text: str) -> Question | str:
        with self._session_factory() as db_session:
            survey = self._repository.get_survey(db_session, survey_id)

            quiz_session = db_session.query(QuizSession).filter_by(
                user_id=user_id, survey_id=survey_id
            ).one_or_none()

            current_question = survey.get_question(quiz_session.current_question_id)
            next_question_id, score_delta = find_next_step(current_question, answer_text)

            if next_question_id == END_OF_SURVEY:
                total_score = quiz_session.score + score_delta
                result_text = survey.get_result_text(total_score)

                db_session.add(
                    QuizResult(
                        user_id=user_id,
                        survey_id=survey_id,
                        total_score=total_score,
                        result_text=result_text,
                    )
                )
                db_session.delete(quiz_session)
                db_session.commit()
                return result_text

            quiz_session.current_question_id = next_question_id
            quiz_session.score += score_delta
            db_session.commit()

            return survey.get_question(next_question_id)