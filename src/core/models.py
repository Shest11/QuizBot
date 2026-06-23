from dataclasses import dataclass, field

@dataclass()
class Answer:
    text: str # текст на кнопке
    next_question_id: str
    score: int = 0

@dataclass()
class Question:
    id: str
    text: str
    question_type: str # тип вопроса (free_text или choice)
    answers: list[Answer] = field(default_factory=list) # создает отдельный список для конкретно этого вопроса
    next_question_id: str | None = None

dataclass()
class ResultRange:
    min_score: int
    max_score: int
    text: str

@dataclass
class Survey:
    id: str
    title: str
    start_question_id: str
    questions: dict[str, Question]
    result_ranges: list[ResultRange] = field(default_factory=list)