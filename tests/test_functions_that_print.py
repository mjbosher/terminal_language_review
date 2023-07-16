import pytest
import google_speech
import script

question_number = 1
verbal_answer = google_speech.Speech("", "En")
lines = list(range(10))
question = "question"
answer = "answer"


class TestPrompt:
    def test_prompt_question_number(self, capfd, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "\n")
        prompt = script.prompt(
            question_number, lines, question, answer, verbal_answer, 3
        )
        out, err = capfd.readouterr()
        assert f"QUESTION ({question_number+1} of {len(lines)})" in out

    def test_prompt_gives_message_on_correct_answer(self, capfd, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda x: "answer")
        prompt = script.prompt(
            question_number, lines, question, answer, verbal_answer, attempts=1
        )
        out, err = capfd.readouterr()
        assert "Correct" in out
        assert not "Wrong" in out

    def test_prompt_gives_message_on_failed_answer(self, capfd, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda x: "incorrect answer\n")
        prompt = script.prompt(
            question_number, lines, question, answer, verbal_answer, attempts=1
        )
        out, err = capfd.readouterr()
        assert "Wrong" in out
        assert not "Correct" in out

    def test_prompt_answer_is_skipped_after_3_attempts(self, capfd, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda x: "incorrect answer\n")
        prompt = script.prompt(
            question_number, lines, question, answer, verbal_answer, attempts=3
        )
        out, err = capfd.readouterr()
        assert "Too many attempts! Moving to next question" in out

    def test_prompt_question_is_printed(self, capfd, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda x: answer)
        prompt = script.prompt(
            question_number, lines, question, answer, verbal_answer, attempts=0
        )
        out, err = capfd.readouterr()
        assert question in out

    def test_prompt_show_reveals_anser(self, capfd, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda x: "show")
        prompt = script.prompt(
            question_number, lines, question, answer, verbal_answer, attempts=1
        )
        out, err = capfd.readouterr()
        assert answer in out


class TestTestFunction:
    languages = {"E": "en"}
    lines = ["E:answer0#question0", "E:answer1#question1", "E:answer2#question2"]

    def test_return_type_is_tuple(self, capfd, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "\n")
        test = script.Test(self.lines, "#", self.languages, audio=False)
        assert isinstance(test, tuple)

    def test_total_is_length_of_file(self, capfd, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "\n")
        score, total, failed_questions = script.Test(
            self.lines, "#", self.languages, audio=False
        )
        assert total == len(self.lines)

    def test_score_is_correct(self, capfd, monkeypatch):
        lines = ["E:answer#question", "E:answer#question", "E:answer#question"]
        monkeypatch.setattr("builtins.input", lambda _: "E:answer")
        score, total, failed_questions = script.Test(
            lines, "#", self.languages, audio=False
        )
        assert score == len(lines)

    def test_delimiter_returns_0_if_invalid(self, capfd, monkeypatch):
        lines = ["E:answer||question", "E:answer||question", "E:answer||question"]
        monkeypatch.setattr("builtins.input", lambda _: "E:answer")
        score, total, failed_questions = script.Test(
            lines, "#", self.languages, audio=False
        )
        assert total == 0

    def test_delimiter_returns_lines_if_valid(self, capfd, monkeypatch):
        lines = ["E:answer||question", "E:answer||question", "E:answer||question"]
        monkeypatch.setattr("builtins.input", lambda _: "E:answer")
        score, total, failed_questions = script.Test(
            lines, "||", self.languages, audio=False
        )
        assert total == len(lines)

    def test_failed_questions_is_equal_to_the_number_of_incorrect_answers(
        self, capfd, monkeypatch
    ):
        lines = ["E:answer||question", "E:answer1||question1", "E:answer2||question2"]
        monkeypatch.setattr("builtins.input", lambda _: "E:answer")
        score, total, failed_questions = script.Test(
            lines, "||", self.languages, audio=False
        )
        assert len(failed_questions) == 2

    def test_failed_questions_return_type_is_set(self, capfd, monkeypatch):
        lines = ["E:answer||question", "E:answer1||question1", "E:answer2||question2"]
        monkeypatch.setattr("builtins.input", lambda _: "E:answer")
        score, total, failed_questions = script.Test(
            lines, "||", self.languages, audio=False
        )
        assert isinstance(failed_questions, set)

    def test_failed_questions_in_list(self, capfd, monkeypatch):
        lines = ["E:answer||question", "E:answer1||question1", "E:answer2||question2"]
        monkeypatch.setattr("builtins.input", lambda _: "E:answer")
        score, total, failed_questions = script.Test(
            lines, "||", self.languages, audio=False
        )
        assert all(
            line in failed_questions
            for line in ["E:answer1||question1", "E:answer2||question2"]
        )

    def test_failed_questions_returned_with_delimiter(self, capfd, monkeypatch):
        lines = ["E:answer||question", "E:answer1||question1", "E:answer2||question2"]
        monkeypatch.setattr("builtins.input", lambda _: "E:answer")
        score, total, failed_questions = script.Test(
            lines, "||", self.languages, audio=False
        )
        assert all("||" in failed_question for failed_question in failed_questions)
