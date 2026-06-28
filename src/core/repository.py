from sqlalchemy import select
from sqlalchemy.orm import Session

from core.db.orm_models import AnswerModel, QuestionModel, SurveyModel
from core.models import Answer, Question, Survey

def build_survey(db_session: Session, survey_id: int) -> Survey:
    survey_row = db_session.get(SurveyModel, survey_id)

    question_rows = db_session.execute(
        select(QuestionModel).where(QuestionModel.survey_id == survey_id)
    ).scalars().all()

    questions: dict[int, Question] = {}

    for question_row in question_rows:
        answers: list[Answer] = []

        if question_row.question_type == "choice":
            answer_rows = db_session.execute(
                select(AnswerModel).where(AnswerModel.question_id == question_row.id)
            ).scalars().all()

            for answer_row in answer_rows:
                answers.append(
                    Answer(
                        text=answer_row.text,
                        next_question_id=answer_row.next_question_id,
                        score=answer_row.score,
                    )
                )

        questions[question_row.id] = Question(
            id=question_row.id,
            text=question_row.text,
            question_type=question_row.question_type,
            answers=answers,
            next_question_id=question_row.next_question_id,
        )

    return Survey(
        id=survey_row.id,
        title=survey_row.title,
        start_question_id=survey_row.start_question_id,
        questions=questions,
    )

def list_surveys(db_session: Session) -> list[Survey]:
    
    survey_rows = db_session.execute(select(SurveyModel)).scalars().all()
    return [build_survey(db_session, survey_row.id) for survey_row in survey_rows]

