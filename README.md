# Terminal Language Review
A CLI based python script for self-reviewing languages and other subjects of interest, making use of the module `cmd` to give an interactive experience as well as incorporating `googletrans` and `google-speech` to allow audio for those words you commonly mispronounce.

Functionality
-------------
-`toggle_audio` or `toggle_log` toggles audio and logs respectively
-`audio on|off` turns audio on or off
-`log on|off` turns the logging of test stats to a `scores.log` file
-`env` view current environment variables
-`load` takes an optional file argument but by default loads environment from `config.ini`
-`save` optional file but by default saves the current environment to `config.ini`
-`set` sets specific environment variables such as adding to the available language codes.
-`stats` view stats from the `scores.log`
-`ls` view current directory , `ls working_directory` to view working directory as per `env` settings
-`make src_file dest_file` returns the additional inverse of the files content to make a complete test.

source file:```
Answer#Question
R:Wine#вино
```
output file:```
Answer#Question
R:Wine#вино
Question#Answer
вино#R:Wine
```    
-`exit` exits script

Set Specific Environment Variables
----------------------------------
Usuage
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
