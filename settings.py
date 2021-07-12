# When editing this file, be sure you use the same syntax as what is given. Anything but integers require quotation marks ("")

# Bot account info. You can change the name, do not change the ID
bot = {
    "name": "Domo",
    "id": 803380541230940161
}

# These should remain unchanged, unless you wish to specify a different folder or file
paths = {
    "trivia": "./data/trivia.json",
    "userdata": "./data/userdata.json",
    "memories": "./resources/memories/"
}

# Channels for the corresponding extension/context to remain in (Trivia can only be done in trivia channel, etc)
# To find your channel ID, enable dev mode in discord, right click your channel, and copy ID
channels = {
    "bot": 803380541230940161,
    "trivia": 863164248607424523,
    "gambling": 863276584730361887
}

trivia = {
    # Money rewarded for 1st, 2nd, and 3rd in trivia game
    "trivia_pay": [50, 35, 20],
    "trivia_rounds": 5,
    "round_time": 20
}

payouts = {
    # XP rewarded per chat message (this will be reworked later)
    "chat_xp": 20,
}
