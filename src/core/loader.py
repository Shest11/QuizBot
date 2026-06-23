import json
from pathlib import Path
from .models import Answer, Question, ResultRange, Survey

class SurveyConfigError(Exception):

    class SurveyBuilder:
        def build_from_file(self, file_path: Path) -> Survey:

            try:
                raw_text = file_path.read_text(encoding="utf-8")
            except OSError as error:
                raise SurveyConfigError(
                    f"Не удалось прочитать файл {file_path}: {error}"
                ) from error

            try:
                raw_data = json.loads(raw_text)
            except json.JSONDecodeError as error:
                raise SurveyConfigError(
                    f"Файл {file_path} содержит невалидный JSON: {error}"
                ) from error

            return self._build_from_dict(raw_data, source_name=str(file_path))

        def _build_from_dict(self, raw_data: dict, source_name: str) -> Survey:

            questions: dict[str, Question] = {} # здесь храним вопросы

            raw_questions = raw_data.get("questions", {})
            for question_id, raw_question in raw_questions.items():
                questions[question_id] = self._build_question(question_id, raw_question)

            result_ranges = []
            for raw_range in raw_data.get("results", []): # raw_range - словарь из списка result
                result_range = ResultRange(
                    min_score=raw_range["min"],
                    max_score=raw_range["max"],
                    text=raw_range["text"],
                )
                result_ranges.append(result_range)

            return Survey(
                id=raw_data["id"],
                title=raw_data["title"],
                start_question_id=raw_data["start_question"],
                questions=questions,
                result_ranges=result_ranges,
            )

        def _build_question(self, question_id: str, raw_question: dict) -> Question:

            question_type = raw_question["type"]

            answers: list[Answer] = []
            if question_type == "choice":
                for raw_answer in raw_question.get("answers", []): # raw_answer - словарь из списка answers
                    answers.append(
                        Answer(
                            text=raw_answer["text"],
                            next_question_id=raw_answer["next"],
                            score=raw_answer.get("score", 0),
                        )
                    )

            return Question(
                id=question_id,
                text=raw_question["text"],
                question_type=question_type,
                answers=answers,
                next_question_id=raw_question.get("next"),
            )