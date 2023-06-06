import os
import sys
import random
from cmd import Cmd
from configparser import ConfigParser
from typing import Optional, Union
from termcolor import colored
import google_speech
from googletrans import Translator
import pendulum


def files(working_dir: str, excludes: list, excludes_ext: list) -> tuple:
    """
    Returns files from the working directory / current directory that meet certain conditions
    """
    working_dir_files: list = [
        file
        for file in os.listdir(working_dir)
        if os.path.isdir(working_dir)
        and file not in excludes
        and all(not file.endswith(ext) for ext in excludes_ext)
    ]

    fileList: list = [
        file
        for file in os.listdir()
        if file not in excludes and all(not file.endswith(ext) for ext in excludes_ext)
    ]
    return (fileList, working_dir_files)


def print_coloured(
    text: str,
    color: str = "blue",
    background: Optional[str] = None,
    end: Optional[str] = "\n" * 2,
    sep: Optional[str] = "\t",
) -> None:
    """prints content to terminal in desired colors"""
    params: tuple = (text, color, background) if background else (text, color)
    formattedText: colored = colored(*params, attrs=["bold"])
    print(formattedText, sep=sep, end=end)


def getFile(
    file: str,
    filelist: list,
    working_dir_files: list,
    working_dir: str,
    mode: str = "r",
) -> list:
    """returns a file in a given mode if the file exists"""
    if file in filelist and not os.path.isdir(file):
        return open(file, mode).readlines()
    elif file in working_dir_files and not os.path.isdir(
        os.path.join(working_dir, file)
    ):
        return open(os.path.join(working_dir, file), mode).readlines()
    else:
        raise IOError("File Not Found")


def getRandomFile(filelist: list, working_dir_files: list, working_dir: str) -> list:
    """Returns a random file from the working_dir_files as a list of it's content"""
    random_filepath: str = random.choice(working_dir_files)
    return getFile(random_filepath, filelist, working_dir_files, working_dir)


def getRandomSelection(
    filelist, working_dir_files: list, working_dir: str, k: int = 3
) -> list:
    """Returns the content of (k) number of files as a concatenated list"""
    lines: list = []
    files: list = random.choices(working_dir_files, k=k)
    for file in files:
        lines += getFile(file, filelist, working_dir_files, working_dir)
    return lines


def speak(
    question: str, answer: str, languages: list, audio: Union[str, bool, None] = None
) -> tuple:
    """
    question = R:To speak
    answer = говорить

    This function splits both the question or answer looking for R:, this is the language codes from
    the languages dictionary defined in the header. This function then returns the answer and question
    in the correct spoken format, ready to be played

    """
    split_question: list = question.split(":")
    split_answer: list = answer.split(":")

    verbal_answer: google_speech.Speech = google_speech.Speech
    verbal_question: google_speech.Speech = google_speech.Speech

    if len(split_question) > 1 and audio:
        return (
            verbal_question(question.split(":")[1], languages["E"]),
            verbal_answer(answer, languages[question.split(":")[0]]),
        )
    elif len(split_answer) > 1 and audio:
        return (
            verbal_question(question, languages[answer.split(":")[0]]),
            verbal_answer(answer.split(":")[1], languages["E"]),
        )
    elif audio:
        return (
            verbal_question(question, languages["E"]),
            verbal_answer(answer, languages["E"]),
        )
    else:
        return (verbal_question("", "en"), verbal_answer("", "en"))


def prompt(
    question_number: int,
    lines: list,
    question: str,
    answer: str,
    verbal_answer: google_speech.Speech,
    attempts: int = 0,
) -> bool:
    """
    Asks the user to answer the given question,
            if correct returns True
            if "show" the answer is printed on the screen then returns false
            if error question is reiterated a maximum of 3 times before returning false

            if verbal_answer is an invoke function then the answer will be played at the
            appropriate time

            if verbal_answer is a reference to an object then no error will be raised and no sound will
            be played
    """
    print_coloured(f"\n\nQUESTION ({question_number+1} of {len(lines)})\n")
    print_coloured(question + "\n")
    user_input: str = input("YOUR ANSWER: ")
    if user_input.replace(" ", "").lower() == answer.replace(" ", "").lower():
        verbal_answer.play()
        print_coloured("Correct", color="green")
        return True

    elif user_input.lower() == "show":
        print_coloured(answer + "\n", color="red")
        verbal_answer.play()

    elif attempts < 3:
        print_coloured("Wrong", color="red")
        return prompt(
            question_number, lines, question, answer, verbal_answer, attempts + 1
        )

    elif attempts == 3:
        print_coloured("Wrong", color="red")
        print_coloured(
            "Too many attempts! Moving to next question", color="yellow", end="\n"
        )
        verbal_answer.play()
    return False


def Test(lines: list, delimiter: str, languages: list, audio: bool = True) -> tuple:
    """
    Takes a list of strings
            e.g. France#Country with a red, white blue flag
                 R:Hello#привет
            The strings correspond to answer#question

    The function then prompts the user to answer the questions
    Returns the number questions correct,total number of questions answered
    and a list of questions which the user got incorrect

    if audio is True then the spoken text is used along side it's written counterpart
    """
    random.shuffle(lines)
    lines: list = [line for line in lines if delimiter in line]
    score: int = 0

    failed_questions: set = set()

    for question_number, line in enumerate(lines):
        attempts: int = 0
        split_line: list = line.strip().split(delimiter)
        question: str = split_line[1]
        answer: str = split_line[0]

        verbal_cues: tuple = speak(question, answer, languages, audio)
        verbal_question: google_speech.Speech = verbal_cues[0]
        verbal_answer: google_speech.Speech = verbal_cues[1]
        verbal_question.play()

        if prompt(question_number, lines, question, answer, verbal_answer):
            score += 1
        else:
            failed_questions.add(line)

    return (score, len(lines), failed_questions)


def writeLog(file: str, correct: int, total: int, log_file: str, log: bool):
    with open(log_file, "a") as open_log_file:
        open_log_file.write(
            f"\n{pendulum.now().strftime('%d/%m/%Y %H:%M')} {file} {correct}/{total} {round((100/total)*correct)}%"
        )
    print_coloured(f"Wrote log for the last test scores in {log_file}")


def writeErrorsToFile(file: str, error_file: str, errors: set):
    """writes errors made in the test to a specified file without duplicate lines"""
    lines: list = []
    if os.path.exists(error_file):
        f = open(error_file, "r")
        lines + f.readlines()
        f.close()

    wf = open(error_file, "w")
    if file != error_file and file.lower() != "random collection":
        lines = set(lines) | errors
    elif file == error_file:
        lines = errors
    for line in lines:
        wf.write(line)
    wf.close()
    print_coloured(f"Wrote Errors to {error_file}", color="cyan")


def score(
    file: str, correct: int, total: int, log_file: str, log: bool, error_file: str
):
    if total > 0:
        print_coloured(f"\nYou scored {correct}/{total}", color="cyan", end="\n")
        print_coloured(
            f"Percent:{round((100/total)*correct)}%", color="yellow", end="\n"
        )
        print_coloured(f"File:s{file}", color="green", end="\n")
        print_coloured(
            f"Date:{pendulum.now().strftime('%d/%m/%Y %H:%M')}", color="yellow"
        )
        if log and file != error_file and file.lower() != "random collection":
            writeLog(file, correct, total, log_file, log)


def remodelFile(src: str, dest: str, delimiter: str = "#"):
    if os.path.exists(src):
        if os.path.exists(dest):
            print_coloured(
                f"{dest} already exists, Type 'overwrite' to overwrite",
                color="red",
                end="",
            )
            overwrite: str = input(": ")
            if "overwrite" not in overwrite.lower():
                raise IOError("Refusing to overwrite")
        data = open(src)
        parsedData = remodelData(data.readlines(), delimiter)
        data.close()
        writeData(dest, parsedData)
        return f"Added inverse data and exported as {dest}"
    else:
        raise IOError(f"{src} file does not exist")


def getLanguage(language: str, languages: list) -> tuple:
    language_key: str = language.rstrip().rsplit("=", 1)[1]
    if language_key in languages:
        language_code: str = languages[language_key]
        return (language_key, language_code)
    return tuple()


def translateFile(
    src: str,
    dest: str,
    languages: list,
    delimiter: str = "#",
    language: Optional[str] = None,
):
    if os.path.exists(src):
        # if dest exists ask whether or not to overwrite it
        if os.path.exists(dest):
            print_coloured(
                f"{dest} already exists, Type 'overwrite' to overwrite",
                color="red",
                end="",
            )
            overwrite: str = input(": ")
            if "overwrite" not in overwrite.lower():
                raise IOError("Refusing to overwrite")

        data = open(src)
        file_data: list = data.readlines()
        # if language, validate it against dictionary keys
        if language:
            code, lang = getLanguage(language, languages)
            translated_data = makeTranslation(file_data, code, lang, delimiter)
            parsedData = remodelData(translated_data, delimiter)
            writeData(dest, parsedData)
            return f"Translated {src} and exported as {dest}"
        # if not language take the first line from the top of the file and if it contains
        # language=code then validate it else raise an error
        elif not language:
            file_header: str = file_data.pop(0)
            if "language" in file_header:
                code, lang = getLanguage(file_header, languages)
                translated_data = makeTranslation(file_data, code, lang, delimiter)
                parsedData = remodelData(translated_data, delimiter)
                writeData(dest, parsedData)
                return f"Translated {src} and exported as {dest}"
            else:
                raise ValueError("No Language Defined in  File Header")
        data.close()
    else:
        print_coloured(f"{src} file does not exist", color="red")


def makeTranslation(data: list, code: str, lang: str, delimiter: str = "#") -> list:
    translated_data: list = []
    for i in data:
        translated_data.append(
            f"{code.capitalize()}:{i.rstrip().capitalize()}{delimiter}{Translator().translate(i,src='en', dest=lang).text}\n"
        )
    return translated_data


def remodelData(data: list, delimiter: str) -> list:
    parsed_data: list = []
    for line in data:
        split_line: list = line.rstrip().split(delimiter)
        if len(split_line) == 2:
            parsed_line: str = split_line[1] + delimiter + split_line[0] + "\n"
            parsed_data.append(parsed_line)
    return parsed_data + data


def writeData(dest: str, data: list):
    f = open(dest, "w")
    for line in data:
        f.write(line)
    f.close()


class CommandLine(Cmd):
    def __init__(self):
        super().__init__()
        self.env = dict(
            audio=False,
            log=True,
            log_file="scores.log",
            error_file="_Errors",
            delimiter="#",
            excludes=[],
            excludes_ext=[".py"],
            working_dir="/home/michael/Downloads/Workarea/DevLearn/Russian/COMPLETE/P1",
            languages={"R": "ru", "E": "en", "U": "uk", "Z": "ZH-cn"},
        )
        self.ruler: str = "-"
        self.prompt: str = "COMMAND >>"
        self.intro: str = "Type help to view commands\n".upper()

    def emptyline(self):
        return self.default()

    def default(self, line=None):
        filelist, working_dir_files = files(
            self.env["working_dir"], self.env["excludes"], self.env["excludes_ext"]
        )

        if line in filelist or line in working_dir_files:
            file: list = getFile(
                line, filelist, working_dir_files, self.env["working_dir"]
            )
        elif line not in filelist and line not in working_dir_files and line:
            print_coloured(f"{line} Not Recognized", color="red")
            return None
        else:
            line: str = "Random Collection"
            file: list = getRandomFile(
                filelist, working_dir_files, self.env["working_dir"]
            )

        results: tuple = Test(
            file, self.env["delimiter"], self.env["languages"], self.env["audio"]
        )
        correct, total, incorrect_questions = results
        score(
            line,
            correct,
            total,
            self.env["log_file"],
            self.env["log"],
            self.env["error_file"],
        )
        writeErrorsToFile(line, self.env["error_file"], incorrect_questions)

    def do_random(self, line=None):
        """returns a random selection of question from the current directory and the working directory"""
        filelist, working_dir_files = files(
            self.env["working_dir"], self.env["excludes"], self.env["excludes_ext"]
        )
        file: list = getRandomSelection(
            filelist, working_dir_files, self.env["working_dir"]
        )
        results: tuple = Test(
            file, self.env["delimiter"], self.env["languages"], self.env["audio"]
        )
        correct, total, incorrect_questions = results
        score(
            line,
            correct,
            total,
            self.env["log_file"],
            self.env["log"],
            self.env["error_file"],
        )

    def do_audio(self, line: str):
        """
        audio on|off toggles the state of the audio for the verbal cues
        """
        if line.lower() == "on" or line.lower() == "true":
            self.env["audio"] = True
        elif line.lower() == "off" or line.lower() == "false":
            self.env["audio"] = False

    def do_toggle_audio(self, line: str):
        """toggles audio on|off"""
        if self.env["audio"] == True:
            self.env["audio"] = False
        else:
            self.env["audio"] = True

    def do_log(self, line: str):
        """
        log on|off
        """
        if line.lower() == "on" or line.lower() == "true":
            self.env["log"] = True
        elif line.lower() == "off" or line.lower() == "false":
            self.env["log"] = False

    def do_toggle_log(self, line: str):
        """toggles log on|off"""
        if self.env["log"] == True:
            self.env["log"] = False
        else:
            self.env["log"] = True

    def do_env(self, line: Optional[str] = None):
        """prints the current environment settings"""
        for name, value in self.env.items():
            print_coloured(name, end=" : ", color="green", background="on_white")
            print_coloured(value, end="\n", color="cyan")

    def do_set(self, line: str):
        """
        Sets the current environment settings
                set [setting_name][value][optional]
                if the setting is a dict, it should be set as
                        set [setting_name][value][key_for_dict]
                if the setting is a list or a set
                        set [setting_name][value][key_for_dict]
                if the setting is a string|int|float
                        set [setting_name][value]
        """
        try:
            key, value, *args = line.split(" ")
            current_env_var: str = self.env.get(key, "")
            if current_env_var:
                print_coloured(f"\nCurrent values:", color="yellow", end=" ")
                print_coloured(current_env_var, color="white")
                if isinstance(current_env_var, dict) and args:
                    self.env[key][args[0]] = value
                    print_coloured("Successfully Updated Environment", "yellow")
                elif isinstance(current_env_var, dict) and not args:
                    print_coloured("\nError:", end=" ", color="red")
                    print_coloured(
                        "The setting is a dictionary but the key has not being specified",
                        color="blue",
                    )
                elif isinstance(current_env_var, list):
                    for items in [value, *args]:
                        self.env[key].append(items)
                    print_coloured("Successfully Updated Environment", "yellow")
                elif isinstance(current_env_var, set):
                    for items in [value, *args]:
                        self.env[key].add(items)
                    print_coloured("Successfully Updated Environment", "yellow")
                else:
                    self.env[key] = value
                    print_coloured("Successfully Updated Environment", "yellow")
            else:
                print_coloured("\nError:", end=" ", color="red")
                print_coloured("Not a valid config key", color="blue")
        except (IndexError, ValueError):
            print_coloured("\nError:", end=" ", color="red")
            print_coloured("Missing the required key or value", color="blue")

    def do_save(self, line: str):
        """saves current environment settings to a file, default filename is 'config.ini'
        save [filename]
        """
        filename: str = "config.ini"
        if line:
            filename: str = line
        config = ConfigParser()
        config["CONFIG"] = self.env

        with open(filename, "w") as conf:
            config.write(conf)
        print_coloured(f"Wrote environment to {filename}", color="green")

    def do_load(self, line):
        """loads a config file into memory, default filename is 'config.ini'
        load [filename]
        """
        filename: str = "config.ini"
        if os.path.exists(line):
            filename: str = line

        config = ConfigParser()
        config.read(filename)
        for key, value in self.env.items():
            if isinstance(value, (list, set, dict)):
                self.env[key] = eval(config.get("CONFIG", key))
            elif isinstance(value, bool):
                self.env[key] = config.getboolean("CONFIG", key)
            elif isinstance(value, int):
                self.env[key] = config.getint("CONFIG", key)
        print_coloured(f"loaded environment from {filename}", color="green")

    def do_ls(self, line: str):
        """lists current directory without arguments
        ls working directory | lists working directory
        """

        filelist, working_dir_files = files(
            self.env["working_dir"], self.env["excludes"], self.env["excludes_ext"]
        )
        if not line:
            print_coloured(filelist, "green")
        elif line.lower() == "working directory":
            print_coloured(working_dir_files, "green")

    def do_stats(self, line):
        """Prints the current log file, results less than 50% are shown in red"""
        if os.path.exists(self.env["log_file"]):
            file = open(self.env["log_file"])
            for line in file:
                percent: list = line.rsplit(" ", 1)
                if len(percent) > 1:
                    percent: str = percent[1].replace("%", "")
                    if float(percent) <= 50:
                        color: str = "red"
                else:
                    color: str = "yellow"
                print_coloured(line, color=color, end="\n")

    def do_make(self, line):
        """
        Returns the inverse data to the current dataset, e.g.
                Answer#Question
                Question#Answer
                вино#R:Wine
                R:Wine#вино
        Command: make src_file dest_file
        """
        files: list = line.split(" ")
        if len(files) == 2:
            src, dest = files
            print_coloured(
                remodelFile(src, dest, delimiter=self.env["delimiter"]), color="cyan"
            )
        else:
            print_coloured("Please providev a src and destination file", color="red")

    def do_automake(self, line):
        """
        automake src_file dest_file
        if the above command is used specify language=code as the first line of your file

        automake src_file dest_file language=code
        In the above case language should not be specified in the file

        file example:
                I speak
                you speak
                he speaks

        This will return:
                Говорить#R:To speak
                я говорю#R:I speak
                Вы говорите#R:You speak
                он говорит#R:He speaks
                R:To speak#Говорить
                R:I speak#я говорю
                R:You speak#Вы говорите
                R:He speaks#он говорит

        """
        lines: list = line.split(" ")

        if len(lines) == 3 and "language" in line:
            # language specified here
            src, dest, language = lines
            print_coloured(
                translateFile(
                    src,
                    dest,
                    self.env["languages"],
                    delimiter=self.env["delimiter"],
                    language=language,
                ),
                color="cyan",
            )

        elif len(lines) == 2:
            src, dest = lines
            print_coloured(
                translateFile(
                    src, dest, self.env["languages"], delimiter=self.env["delimiter"]
                ),
                color="cyan",
            )

        else:
            print_coloured("Please provide a src and destination file", color="red")

    def do_exit(self, line):
        """terminates the program"""
        sys.exit(0)


CommandLine().cmdloop()
# Next step is to allow code access to sub directories so that there is no need to run this script from each sub directory and so that all errors and scores get added to one place instead of the sub directory equivalent
