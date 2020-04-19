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
import operator


# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Top10"
Website = "https://github.com/czlowiekimadlo/streamlabs-scripts"
Creator = "CzlowiekImadlo"
Version = "1.0"
Description = "Top currency owners"


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
            self.Command = "!top"
            self.TopSize = "5"

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
        data = get_top_scores()
        send_top_response(data)
    return


def Tick():
    """Required tick function."""
    return


# ---------------------------------------
# Logic functions
# ---------------------------------------
def get_top_scores():
    """Get top scores."""
    amount = int(ScriptSettings.TopSize)
    return Parent.GetTopCurrency(amount)


def send_top_response(data):
    """Top scores."""
    position = len(data)
    entry = "{0}. {1} - {2}"
    top_scores = []

    sorted_data = sorted(data.items(), key=operator.itemgetter(1))

    for row in sorted_data:
        top_scores.insert(0, entry.format(position, row[0], row[1]))
        position -= 1

    Parent.SendStreamMessage("\n".join(top_scores))
    return
