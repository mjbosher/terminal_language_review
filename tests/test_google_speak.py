import pytest
import google_speech
import script

question = "E:Testing"
answer = "Testing"
languages = {"E": "en"}


class TestSpeak:
    def test_speak_return_is_tuple(self):
        speak = script.speak(question, answer, languages, True)
        assert isinstance(speak, tuple)

    def test_speak_question_is_google_speech_obj(self):
        speak = script.speak(question, answer, languages, True)
        assert isinstance(speak[0], google_speech.Speech)

    def test_speak_answer_is_google_speech_obj(self):
        speak = script.speak(question, answer, languages, True)
        assert isinstance(speak[1], google_speech.Speech)
