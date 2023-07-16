import script
import os
import pytest
import pendulum

log_file = "test_log.txt"
error_file = "test_errors.txt"
errors = {"answer#question\n", "answer1#question1\n"}


@pytest.fixture
def writeLog():
    yield script.writeLog("mockTest", 3, 10, log_file, True)
    os.remove(log_file)


@pytest.fixture
def writeErrorsToFile():
    yield script.writeErrorsToFile("MockTest", error_file, errors)
    os.remove(error_file)


class TestWriteLog:
    def test_log_file_exists(self, writeLog):
        assert os.path.exists(log_file)

    def test_log_file_content(self, writeLog):
        expected_str = f"mockTest 3/10 {round((100/10)*3)}%"
        assert open(log_file).readlines()[1].endswith(expected_str)


class TestWriteErrorsToFile:
    def test_error_file_exists(self, writeErrorsToFile):
        assert os.path.exists(error_file)

    def test_all_errors_in_error_file(self, writeErrorsToFile):
        assert all(error in open(error_file).readlines() for error in errors)
