#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Command for transferring currency to other viewers, for a fee"""
#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import json
import os
import math
#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Give"
Website = "https://github.com/czlowiekimadlo/streamlabs-scripts"
Creator = "CzlowiekImadlo"
Version = "1.0"
Description = "Currency transfer"
#---------------------------------------
# Variables
#---------------------------------------
settingsfile = os.path.join(os.path.dirname(__file__), "settings.json")
#---------------------------------------
# Classes
#---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsfile=None):
        if settingsfile and os.path.isfile(settingsfile):
            with codecs.open(settingsfile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else: #set variables if no custom settings file is found
            self.OnlyLive = False
            self.Command = "!give"
            self.SuccessResponse = "{0} has transferred {1} {2} to {3}"
            self.FailResponse = "{0} does not have enough {1} to transfer {2} ({3} fee)"
            self.InactiveResponse = "{0} is not currently active."
            self.Fee = 2

    # Reload settings on save through UI
    def Reload(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')

    def Save(self, settingsfile):
        """ Save settings contained within to .json and .js settings files. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except ValueError:
            Parent.Log(ScriptName, "Failed to save settings to file.")

#---------------------------------------
# Settings functions
#---------------------------------------
def ReloadSettings(jsonData):
    """Reload settings on pressing the save button"""
    global ScriptSettings
    ScriptSettings.Reload(jsonData)

def SaveSettings():
    """Save settings on pressing the save button"""
    Settings.Save(ScriptSettings, settingsfile)

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    """data on Load, required function"""
    global ScriptSettings
    ScriptSettings = Settings(settingsfile)

def Execute(data):
    """Required Execute data function"""
    ChatInput = data.GetParam(0)
    if data.IsChatMessage() and ChatInput.lower() == ScriptSettings.Command.lower():
        if not HasEnoughCurrency(data):
            SendFailResponse(data)
            return

        TransferFunds(data)
    return

def Tick():
    """Required tick function"""
    return

#---------------------------------------
# Logic functions
#---------------------------------------

def HasEnoughCurrency(data):
    """Returns true if user has enough currency"""
    amount = int(data.GetParam(2))
    fee = CalculateFee(amount)
    wealth = int(Parent.GetPoints(data.User))

    if wealth < amount + fee or amount < 0:
        return False
    return True


def SendFailResponse(data):
    """Fail"""
    currency = Parent.GetCurrencyName()
    amount = int(data.GetParam(2))
    fee = CalculateFee(amount)
    Message = ScriptSettings.FailResponse.format(data.UserName, currency, amount, fee)
    Parent.SendStreamMessage(Message)
    return


def TransferFunds(data):
    """Success"""
    currency = Parent.GetCurrencyName()
    targetUser = data.GetParam(1)
    amount = data.GetParam(2)
    fee = CalculateFee(amount)

    transferStatus = Parent.AddPoints(targetUser.lower(), targetUser, long(amount))

    if not transferStatus:
        Message = ScriptSettings.InactiveResponse.format(targetUser)
        Parent.SendStreamMessage(Message)
        return

    Parent.RemovePoints(data.User, data.UserName, int(amount) + int(fee))
    Message = ScriptSettings.SuccessResponse.format(data.UserName, amount, currency, targetUser)
    Parent.SendStreamMessage(Message)
    return

def CalculateFee(amount):
    """Calculate fee for a given amount"""
    FeeBase = 0.01
    TransferRate = FeeBase * ScriptSettings.Fee
    if TransferRate > 0:
        TransferFee = float(amount) * TransferRate
        return math.ceil(TransferFee)
    return 0

