I am writing a script that uses the OpenAI text-davinci-003 model to help the user fix their code given either a traceback or test runner output. Help me write a `Controller` class that maintains state and calls the AI using prompts multiple times using the logic below to achieve the goal of producing a git patch that will fix the error.

First, the Controller is initialized with the command that was run as well as the `stdout` and `stderr`.

The first thing the Controller will do is information gathering. It will use the AI to figure out what information to gather. It will use a prompt that tells the AI it call the controller back with three commands:

- LIST_FILES_IN_DIRECTORY(path_to_directory)
- CAT_FILE(path_to_file)
- GREP(search_string, path)

I have already implemented this.

Then, the controller with ask the AI, in a separate request with the information that has been gathered, to figure out what the issue is and to explain it step by step in detail. We need to format the gathered information cleanly in this new prompt. We should also give context about all the previous stuff that happened (the outputs, the commands that ran with the results, etc.)

Finally, once the issue has been figured out, the controller will ask the AI for a git patch that it can use to fix the error. It will test the patch to make sure it is valid. If not, it will show the AI what the error is and use it to fix the patch until it works.
