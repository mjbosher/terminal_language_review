# Terminal Language Review
A CLI based python script for self-reviewing languages and other subjects of interest, making use of the module `cmd` to give an interactive experience as well as incorporating `googletrans` and `google-speech` to allow audio for those words you commonly mispronounce.

Functionality
-------------
To use this script type a valid filename to iterate over it and it will then log the score and keep track of the errors. When the error file is iterated over, errors which have been correctly entered will be removed from the error file. If `Enter` is pressed without giving a filename, a random file will be choosen but not logged or tracked

* `toggle_audio` or `toggle_log` toggles audio and logs respectively
* `audio on|off` turns audio on or off
* `log on|off` turns the logging of test stats to a `scores.log` file
* `env` view current environment variables
* `load` takes an optional file argument but by default loads environment from `config.ini`
* `save` optional file but by default saves the current environment to `config.ini`
* `set` sets specific environment variables such as adding to the available language codes.
* `stats` view stats from the `scores.log`
* `ls` view current directory , `ls working_directory` to view working directory as per `env` settings
* `make src_file dest_file` returns the additional inverse of the files content to make a complete test.

source file:
```
Answer#Question
R:Wine#вино
```
output file:
```
Answer#Question
R:Wine#вино
Question#Answer
вино#R:Wine
```
* `automake src_file dest_file language=code` languae is an optional argument and if left out should be specified in the first line of the src_file `language= language_code`, followed by a list of the target vocabulary to be iterated over
* `random` - takes a selection of random files from the files in the current and the working directory. Random is not added to the logs and nor are the errors tracked     
* `exit` exits script

File Format
-----------
The standard file format is a csv file using `#` as the delimiter. The delimiter can be changed by using `set delimiter new_delimiter` e.g. `set delimiter ,` to set the delimiter to a comma. 
```
Answer#Question
```

For processing the laguages, a word is prepended with code from the languages dictionary 
e.g. `R:Wine#вино` means that the Question `вино` will be spoke in Russian by google speak

The language codes can be modified by doing `set languages S es` - `S` being your personal choice for easy to remember codes and `es` being the required google code which can be found [here](https://developers.google.com/admin-sdk/directory/v1/languages)


Usage
------
To run the script:
```
python3 script.py
```

for help after running the script type `help` or `help command` replacing command with that which you are querying about

Installation
------------

To install the must be a valid python cadidate installed on the target machine as well as `SoX` in order to use the audio functionality that comes with `google-speech` for more information about installing `SoX` please see the aformentioned modules [homepage](https://pypi.org/project/google-speech/)

```
pip3 install -r requirements.txt
``` 

Set Specific Environment Variables
----------------------------------
* `set delimiter new_delimiter` - sets a new delimiter 
* `set languages your_code google_code` - adds to the language codes as mentioned above in `file format`
* `set log_file filename` - sets the name of the log file
* `set error_file filename` -sets the name of the error file
* `set excludes_ext .txt .js` -sets a list of files to be excluded from the filelist
