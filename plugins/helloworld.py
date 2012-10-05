#! /usr/bin/python2
# -*- coding: utf-8 -*-

""" helloworld.py
    plugins.helloworld
    
    a demo plugin
    greets the world
    This is an example of a simple plugin that adds a single command.
    
    Plugin structure:
    A plugin is essentially a python module that defines a single function called
    Init that returns the following tuple:
    
        cmd_string      - command string
        cmd_handler     - command handler function
        generic_handler - generic command handler function or none
    
    cmd_handler(bot, mess, args):
        gets called whenever %{cmd_string} command needs to be executed
        bot     - raw instance of ChmobotJabberBot
        mess    - raw instance of xmpp.protocol.message
        args    - list of command arguments
    generic_handler(bot, mess, cmd, args):
        gets called in cycle whenever an unknown command is executed
        if current plugin is able to parse the unknown command,
        it should return some non-False-like value and the parsing stops
        cmd     - command string
    
    Using generic_handler is not advised, and if not used, generic_handler 
    can be defined as None for a slight speed improvement
"""

def Init(bot):
    cmd = 'helloworld'
    def command_helloworld(bot, mess, args):
        """Greets the world"""
        return "Hello, world!"
    #def unknown_command(bot, mess, cmd, args)
    #    """no generic command handler"""
    #    return None
    return (cmd, command_helloworld, None)
