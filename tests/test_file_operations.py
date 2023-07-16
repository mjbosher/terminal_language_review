import pytest
import os
import io
import shutil
import script


@pytest.fixture(scope="class")
def files():
    test_dir = "files"
    pytest.excludes = ["test.ini"]
    pytest.excludes_ext = [".txt"]
    os.mkdir(test_dir)
    files = ["test.txt", "test.ini", "test"]

    for file in files:
        os.mknod(os.path.join(test_dir, file))
        os.mknod(file)
    yield (script.files(test_dir, pytest.excludes, pytest.excludes_ext))

    shutil.rmtree(test_dir)
    for file in files:
        os.remove(file)


class TestFilesFromWorkingDirectory:
    def test_working_dir_has_only_1_file(self, files):
        assert len(files[1]) == 1

    def test_working_dir_does_not_contain_excluded_files(self, files):
        assert all(file not in files[1] for file in pytest.excludes)

    def test_working_dir_excludes_files_with_excluded_extensions(self, files):
        assert all(
            not file.startswith(ext) for file in files[1] for ext in pytest.excludes
        )

    def test_working_dir_return_is_list(self, files):
        assert isinstance(files[1], list)


class TestFilesFromCurrentDirectory:
    def test_current_dir_does_not_contain_excluded_files(self, files):
        assert all(file not in files[0] for file in pytest.excludes)

    def test_current_dir_excludes_files_with_excluded_extensions(self, files):
        assert all(
            not file.startswith(ext) for file in files[0] for ext in pytest.excludes
        )

    def test_current_dir_return_is_list(self, files):
        assert isinstance(files[0], list)


class TestGetFiles:
    def test_getFiles_returns_list(self, files):
        getFile = script.getFile("test", files[0], files[1], ".", mode="r")
        assert isinstance(getFile, list)

    def test_getFiles_does_not_return_excluded_fiiles(self, files):
        try:
            getFile = script.getFile("test.ini", files[0], files[1], ".", mode="r")
        except Exception as e:
            assert e.args[0] == "File Not Found"

    def test_getFiles_does_not_raises_error_if_file_not_found(self, files):
        try:
            getFile = script.getFile(
                "not_a_file.txt", files[0], files[1], ".", mode="r"
            )
        except Exception as e:
            assert e.args[0] == "File Not Found"


class Test_getRandomSelection:
    def test_getRandomSelection_returns_list(self, files):
        getRandomSelection = script.getRandomSelection(files[0], files[1], ".")
        assert isinstance(getRandomSelection, list)
