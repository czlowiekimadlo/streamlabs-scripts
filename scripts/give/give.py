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
            self.OnlyLive = True
            self.Command = "!give"
            self.SuccessResponse = "{0} won {1} {3} and now has {2} {3} "
            self.FailResponse = "A raffle for {0} {1} has started! Type !join to join."

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
# Optional functions
#---------------------------------------
def SendResp(data, Usage, Message):
    """Sends message to Stream or discord chat depending on settings"""
    Message = Message.replace("$user", data.UserName)
    Message = Message.replace("$currencyname", Parent.GetCurrencyName())
    Message = Message.replace("$target", data.GetParam(1))
    Message = Message.replace("$permissioninfo", MySet.PermissionInfo)
    Message = Message.replace("$permission", MySet.Permission)

    l = ["Stream Chat", "Chat Both", "All", "Stream Both"]
    if not data.IsFromDiscord() and (Usage in l) and not data.IsWhisper():
        Parent.SendStreamMessage(Message)

    l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
    if not data.IsFromDiscord() and data.IsWhisper() and (Usage in l):
        Parent.SendStreamWhisper(data.User, Message)

    l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
    if data.IsFromDiscord() and not data.IsWhisper() and (Usage in l):
        Parent.SendDiscordMessage(Message)

    l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
    if data.IsFromDiscord() and data.IsWhisper() and (Usage in l):
        Parent.SendDiscordDM(data.User, Message)

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    """data on Load, required function"""
    global ScriptSettings
    ScriptSettings = Settings(settingsfile)

def Execute(data):
    """Required Execute data function"""
    if State == 0 and data.IsChatMessage() and data.GetParam(0).lower() == MySet.Command.lower():

        if not HasPermission(data):
            return

        if not MySet.OnlyLive or Parent.IsLive():
            State = 1
            WinAmount = data.GetParam(1)
            message = MySet.StartResponse.format(WinAmount, Parent.GetCurrencyName())
            SendResp(data, MySet.Usage, message)
            StartTime = time.time()
            StartData = data
            return

    if State == 1 and data.IsChatMessage() and data.GetParam(0).lower() == MySet.JoinCommand.lower():
        JoinedPlayers.append(data)
        SendResp(data, MySet.Usage, MySet.JoinMessage)
        return
    return

def PickWinner(data):
    global State
    global JoinedPlayers
    global StartTime
    global WinAmount

    State = 0
    StartTime = None
    if not JoinedPlayers:
        SendResp(data, MySet.Usage, MySet.NoJoinResponse)
        return

    secure_random = random.SystemRandom()
    PickedPlayer = secure_random.choice(JoinedPlayers)
    currency = Parent.GetCurrencyName()
    Parent.AddPoints(PickedPlayer.User, PickedPlayer.UserName, int(WinAmount))
    points = Parent.GetPoints(PickedPlayer.User)
    winMessage = MySet.WinResponse.format(PickedPlayer.UserName, WinAmount, points, currency)
    SendResp(data, MySet.Usage, winMessage)
    JoinedPlayers = []
    return

def Tick():
    """Required tick function"""
    return

def HasPermission(data):
    """Returns true if user has permission and false if user doesn't"""
    if not Parent.HasPermission(data.User, MySet.Permission, MySet.PermissionInfo):
        message = MySet.PermissionResp.format(data.UserName, MySet.Permission, MySet.PermissionInfo)
        SendResp(data, MySet.Usage, message)
        return False
    return True
