GiveAwayBot

This Python script allows you to conduct a giveaway among the commentators of a post in Telegram. You can specify the number of winners and a phrase that must be included in the comment of the participant. The script also ensures that each participant is only considered once, so the chances of winning are not affected by the number of comments left.

Telegram Bot API does not allow retrieving the list of commentators through a link, so this solution uses regular Telegram API. You can use your account or purchase an anonymous one at https://fragment.com/numbers (an official platform from Telegram creators).

To get started, fill out the config.yaml file. The file specifies the fields and their purpose.

The script can be used on any operating system with Python installed. You can download Python for Windows from https://www.python.org/downloads/windows/.

If you want to run GiveAwayBot as an exe program, you can use the one that I have already compiled [(download here)](https://github.com/EhrmannGit/giveawaybot/releases) or compile it yourself using the `pyinstaller` package following this instruction: https://datatofish.com/executable-pyinstaller/.

### config.yaml must be in a folder with exe file!
To run the program as a script, follow these steps:

Create a virtual Python environment using the following command:

```
python -m venv env
```

Activate the virtual environment by running the command below:

For Linux/macOS:
```
source venv/bin/activate
```

For Windows:
Run Powershell as admin. Execute command:
```
Set-ExecutionPolicy RemoteSigned
```
Print "y" and press Enter. Run
```
env\Scripts\activate
```
Install the required dependencies using the following command:
```
pip install -r requirements.txt
```
Start the script by running the following command:
```
python giveawaybot.py
```

After starting the program, it will prompt you to enter your phone number, and then the authorization code that you will receive from Telegram.

Upon successful authorization, the bot is ready to work. It will respond to messages in the group whose ID you specified in the config.yaml file.

Expected message structure:
```
https://t.me/{{channel_id}}/{{post_id}}

winners: {{number of winners}}
phrase_to_check: {{phrase that should be in the comment}}
```

The phrase_to_check field can be omitted. In this case, any comment will be taken into account.

