import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src")) # src становится путем для импорта, чтобы перейти в core.db.

from core.db.database import create_db_engine, create_session_factory, init_db
from core.db.orm_models import AnswerModel, QuestionModel, SurveyModel, ResultRangeModel


def seed_anxiety_test(db_session)-> None:
    # тест на тревожность (пример)
    existing = db_session.query(SurveyModel).filter_by(title="Тест на уровень тревожности").first()

    if existing is not None:
        print("Тест на тревожность уже есть в БД, пропускаем")
        return

    survey = SurveyModel(title="Тест на уровень тревожности", start_question_id=0)
    db_session.add(survey)
    db_session.flush() # нужно, чтобы получить survey.id

    q1 = QuestionModel(survey_id=survey.id, text="Как часто вы чувствуете беспокойство без явной причины?", question_type="choice")
    q2 = QuestionModel(survey_id=survey.id, text="Расскажите своими словами, что вас беспокоит", question_type="free_text")
    q3 = QuestionModel(survey_id=survey.id, text="Тяжело ли вам уснуть из-за тревожных мыслей?", question_type="choice")
    db_session.add_all([q1, q2, q3])
    db_session.flush()  # нужно, чтобы получить id вопросов

    survey.start_question_id = q1.id
    q2.next_question_id = q3.id

    db_session.add_all([
        AnswerModel(question_id=q1.id, text="Никогда", next_question_id=q2.id, score=0),
        AnswerModel(question_id=q1.id, text="Иногда", next_question_id=q2.id, score=1),
        AnswerModel(question_id=q1.id, text="Часто", next_question_id=q2.id, score=2),
        AnswerModel(question_id=q3.id, text="Нет", next_question_id=0, score=0),  # 0 = конец опроса
        AnswerModel(question_id=q3.id, text="Да", next_question_id=0, score=2),
    ])

    db_session.add_all([
        ResultRangeModel(survey_id=survey.id, min_score=0, max_score=2, text="У вас низкий уровень тревожности, всё хорошо."),
        ResultRangeModel(survey_id=survey.id, min_score=3, max_score=5, text="Есть признаки повышенной тревожности, стоит отдохнуть."),
    ])
    db_session.commit()
    print("Тест на тревожность добавлен в БД")


def seed_feedback_form(db_session)-> None:
    # анкета обратной связи (пример)
    existing = db_session.query(SurveyModel).filter_by(title="Анкета обратной связи").first()
    if existing is not None:
        print("Опрос 'Анкета обратной связи' уже есть в БД, пропускаем")
        return

    survey = SurveyModel(title="Анкета обратной связи", start_question_id=0)
    db_session.add(survey)
    db_session.flush()

    q1 = QuestionModel(survey_id=survey.id, text="Что вам понравилось больше всего?", question_type="free_text")
    q2 = QuestionModel(survey_id=survey.id, text="Порекомендовали бы нас друзьям?", question_type="choice")
    db_session.add_all([q1, q2])
    db_session.flush()

    survey.start_question_id = q1.id
    q1.next_question_id = q2.id

    db_session.add_all([
        AnswerModel(question_id=q2.id, text="Да", next_question_id=0, score=0),
        AnswerModel(question_id=q2.id, text="Нет", next_question_id=0, score=0),
    ])
    db_session.commit()
    print("Анкета обратной связи добавлен в БД")

def main() -> None:
    db_engine = create_db_engine("quizbot.db")
    init_db(db_engine)
    session_factory = create_session_factory(db_engine)

    with session_factory() as db_session:
        seed_anxiety_test(db_session)
        seed_feedback_form(db_session)

if __name__ == "__main__":
    main()



