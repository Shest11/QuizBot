import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src")) # src становится путем для импорта, чтобы перейти в core.db.

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.database import Base
from core.db.orm_models import SurveyModel, QuestionModel, AnswerModel, ResultRangeModel
from core.engine import SurveyEngine


@pytest.fixture
def memory_db():
    # создаем чистую БД для изоляции
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    with session_factory() as session:
        # создаем сам опрос
        session.add(SurveyModel(id=1, title="Тест тревожности", start_question_id=1))

        # вопрос 1 (от него идет развилка на вопрос 2 или вопрос 3)
        session.add(QuestionModel(id=1, survey_id=1, text="Вам страшно?", question_type="choice"))
        session.add(AnswerModel(id=1, question_id=1, text="Да", next_question_id=2, score=5))
        session.add(AnswerModel(id=2, question_id=1, text="Нет", next_question_id=3, score=1))

        # вопрос 2 (свободный текст).
        session.add(QuestionModel(id=2, survey_id=1, text="Опишите ваш страх:", question_type="free_text", next_question_id=0))

        # вопрос 3 (свободный текст).
        session.add(QuestionModel(id=3, survey_id=1, text="Почему вы так спокойны?", question_type="free_text", next_question_id=0))

        # вилка результатов
        session.add(ResultRangeModel(survey_id=1, min_score=0, max_score=2, text="Результат: Всё отлично"))
        session.add(ResultRangeModel(survey_id=1, min_score=3, max_score=10, text="Результат: Стресс"))

        session.commit()

    return session_factory


def test_list_and_start_survey(memory_db):
    # проверяем вывод списка и старт опроса
    engine = SurveyEngine(session_factory=memory_db)

    surveys = engine.list_available_surveys()
    assert len(surveys) == 1
    assert surveys[0].title == "Тест тревожности"

    first_question = engine.start_survey(user_id=777, survey_id=1)
    assert first_question.id == 1
    assert first_question.text == "Вам страшно?"


def test_graph_branching_yes(memory_db):
    # проверяем переход по графу при ответе 'Да'
    engine = SurveyEngine(session_factory=memory_db)
    engine.start_survey(user_id=777, survey_id=1)

    next_question = engine.answer(user_id=777, survey_id=1, answer_text="Да")
    assert next_question.id == 2
    assert next_question.text == "Опишите ваш страх:"


def test_graph_branching_no(memory_db):
    # проверяем переход по графу при ответе 'Нет'
    engine = SurveyEngine(session_factory=memory_db)
    engine.start_survey(user_id=777, survey_id=1)

    next_question = engine.answer(user_id=777, survey_id=1, answer_text="Нет")
    assert next_question.id == 3
    assert next_question.text == "Почему вы так спокойны?"


def test_final_score_calculation(memory_db):
    # проверяем пошаговый проход и фиксацию ответа пользователя
    engine = SurveyEngine(session_factory=memory_db)
    engine.start_survey(user_id=777, survey_id=1)

    # отвечаем на первый вопрос 'Да'
    next_q = engine.answer(user_id=777, survey_id=1, answer_text="Да")
    assert next_q.id == 2
    assert next_q.text == "Опишите ваш страх:"

    # отвечаем на free_text вопрос
    final_result = engine.answer(user_id=777, survey_id=1, answer_text="Мне очень страшно")

    # проверяем, что это строка (результат), а не вопрос
    assert isinstance(final_result, str)

    # проверяем, что результат соответствует набранным баллам
    assert final_result == "Результат: Стресс"