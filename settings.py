# When editing this file, be sure you use the same syntax as what is given. Anything but integers require quotation marks ("")

bot = {     # Bot account info. You can change the name, do not change the ID
    "name": "Domo",
    "id": 803380541230940161
}

payouts = {  # Money or XP rewards for certain actions
    "chat_xp": 20,    # XP rewarded per chat message
    "trivia_money": 15   # Money rewarded for correct trivia answers
}

paths = {   # These should remain unchanged, unless you wish to specify a different folder or file
    "trivia": "./data/trivia.json",
    "userdata": "./data/userdata.json",
    "memories": "./resources/memories/"
}

channels = {    # Channel for the corresponding extension/context to remain in (Trivia can only be done in trivia channel, etc)
                # To find your channel ID, enable dev mode in discord, right click your channel, and copy ID
    "bot": 803380541230940161,
    "trivia": 863164248607424523,
    "gambling": 863276584730361887
}
