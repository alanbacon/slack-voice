Runs on OS X only. Tested on Yosemite only.

Create a file called `slackToken`:

    touch slackToken

Get your slack API token from here:

    https://api.slack.com/docs/oauth-test-tokens

Place your token as a single line in your `slackToken` file.

Give the python file execute permissions if it doesn't have them already:

    sudo chmod u+x ./slack_voice.py

Run the script:

    ./slack_voice.py quickDemo

Options include:

    quickDemo       : last 50 messages from the experiences channel + any new messages
    wallsHaveEars   : Barbara paranoid that objects are listening to her
    <channel_name>  : new messages from the specified channel name
