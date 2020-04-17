#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Command for transferring currency to other viewers, for a fee."""
# ---------------------------------------
# Libraries and references
# ---------------------------------------
import codecs
import json
import os
import math


# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Give"
Website = "https://github.com/czlowiekimadlo/streamlabs-scripts"
Creator = "CzlowiekImadlo"
Version = "1.0"
Description = "Currency transfer"


# ---------------------------------------
# Variables
# ---------------------------------------
settingsfile = os.path.join(os.path.dirname(__file__), "settings.json")


# ---------------------------------------
# Classes
# ---------------------------------------
class Settings:
    """Loads settings from file if file is found if not uses default values."""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsfile=None):
        """Constructor method."""
        if settingsfile and os.path.isfile(settingsfile):
            with codecs.open(settingsfile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else:  # set variables if no custom settings file is found
            self.OnlyLive = False
            self.Command = "!give"
            self.SuccessResponse = "{0} has transferred {1} {2} to {3}"
            self.FailResponse = "{0} does not have enough {1} to transfer {2} ({3} fee)"
            self.InvalidResponse = "{0} is not a valid amount."
            self.InactiveResponse = "{0} is not currently active."
            self.Fee = 2

    # Reload settings on save through UI
    def Reload(self, data):
        """Reload settings on save through UI."""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')

    def Save(self, settingsfile):
        """Save settings contained within to .json and .js settings files."""
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except ValueError:
            Parent.Log(ScriptName, "Failed to save settings to file.")


# ---------------------------------------
# Settings functions
# ---------------------------------------
def ReloadSettings(json_data):
    """Reload settings on pressing the save button."""
    global ScriptSettings
    ScriptSettings.Reload(json_data)


def SaveSettings():
    """Save settings on pressing the save button."""
    Settings.Save(ScriptSettings, settingsfile)


# ---------------------------------------
# [Required] functions
# ---------------------------------------
def Init():
    """Data on Load, required function."""
    global ScriptSettings
    ScriptSettings = Settings(settingsfile)


def Execute(data):
    """Required Execute data function."""
    chat_input = data.GetParam(0)
    if data.IsChatMessage() and chat_input.lower() == ScriptSettings.Command.lower():
        if not is_request_correct(data):
            send_invalid_response(data)
            return

        if not has_enough_currency(data):
            send_fail_response(data)
            return

        transfer_funds(data)
    return


def Tick():
    """Required tick function."""
    return


# ---------------------------------------
# Logic functions
# ---------------------------------------
def is_request_correct(data):
    """Validate if request even makes sense."""
    amount = int(data.GetParam(2))

    if amount > 0:
        return True
    return False


def has_enough_currency(data):
    """Return true if user has enough currency."""
    amount = int(data.GetParam(2))
    fee = calculate_fee(amount)
    wealth = int(Parent.GetPoints(data.User))

    if wealth < amount + fee or amount < 0:
        return False
    return True


def send_fail_response(data):
    """Fail."""
    currency = Parent.GetCurrencyName()
    amount = int(data.GetParam(2))
    fee = calculate_fee(amount)
    message = ScriptSettings.FailResponse.format(data.UserName, currency, amount, fee)
    Parent.SendStreamMessage(message)
    return


def send_invalid_response(data):
    """Fail."""
    amount = int(data.GetParam(2))
    message = ScriptSettings.InvalidResponse.format(amount)
    Parent.SendStreamMessage(message)
    return


def transfer_funds(data):
    """Success."""
    currency = Parent.GetCurrencyName()
    target_user = data.GetParam(1)
    amount = data.GetParam(2)
    fee = calculate_fee(amount)

    transfer_status = Parent.AddPoints(target_user.lower(), target_user, long(amount))

    if not transfer_status:
        message = ScriptSettings.InactiveResponse.format(target_user)
        Parent.SendStreamMessage(message)
        return

    Parent.RemovePoints(data.User, data.UserName, int(amount) + int(fee))
    message = ScriptSettings.SuccessResponse.format(data.UserName, amount, currency, target_user)
    Parent.SendStreamMessage(message)
    return


def calculate_fee(amount):
    """Calculate fee for a given amount."""
    fee_base = 0.01
    transfer_rate = fee_base * ScriptSettings.Fee
    if transfer_rate > 0:
        transfer_fee = float(amount) * transfer_rate
        return math.ceil(transfer_fee)
    return 0
