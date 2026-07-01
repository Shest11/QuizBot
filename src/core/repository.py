from sqlalchemy import select
from sqlalchemy.orm import Session

from core.db.orm_models import AnswerModel, QuestionModel, SurveyModel, ResultRangeModel
from core.models import Answer, Question, Survey, ResultRange


class SurveyRepository:

    def get_survey(self, db_session: Session, survey_id: int) -> Survey:
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

        range_rows = db_session.execute(select(ResultRangeModel).where(ResultRangeModel.survey_id == survey_id)).scalars().all()

        result_ranges = [ResultRange(min_score=r.min_score, max_score=r.max_score, text=r.text) for r in range_rows]

        return Survey(
            id=survey_row.id,
            title=survey_row.title,
            start_question_id=survey_row.start_question_id,
            questions=questions,
            result_ranges=result_ranges,
        )

    def list_surveys(self, db_session: Session) -> list[Survey]:

        # вернуть список всех опросов, которые есть в БД прямо сейчас

        survey_rows = db_session.execute(select(SurveyModel)).scalars().all()
        return [self.get_survey(db_session, survey_row.id) for survey_row in survey_rows]