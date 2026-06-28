from dataclasses import dataclass, field


@dataclass
class Answer:
    text: str  # текст на кнопке
    next_question_id: int
    score: int = 0


@dataclass
class Question:
    id: int
    text: str
    question_type: str  # тип вопроса (free_text или choice)
    answers: list[Answer] = field(default_factory=list)  # создаёт отдельный список для конкретно этого вопроса
    next_question_id: int | None = None


@dataclass
class ResultRange:
    min_score: int
    max_score: int
    text: str


@dataclass
class Survey:
    id: int
    title: str
    start_question_id: int
    questions: dict[int, Question]
    result_ranges: list[ResultRange] = field(default_factory=list)

    def get_question(self, question_id: int) -> Question:
        return self.questions[question_id]

    def get_result_text(self, total_score: int) -> str:
        for result_range in self.result_ranges:
            if result_range.min_score <= total_score <= result_range.max_score:
                return result_range.text
        return "Опрос завершён, спасибо за ответы!"