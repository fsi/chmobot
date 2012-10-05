#! /usr/bin/python2
# -*- coding: utf-8 -*-

""" debug.py
    plugins.debug
    
    a debug plugin
    for debugging purposes
    This is more complex example of a stateful plugin with generic message handler
    

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

class MyStatefulDebug:
    def __init__(self, dbg=True):
        self._is_debug_on = dbg
        
    def __call__(self, *args, **kwargs):
        if len(args) == 3:
            # called as a "%debug args" parser
            if args[2] and args[2].lower() == 'on':
                self._is_debug_on = True
            elif args[2] and args[2].lower() == 'off':
                self._is_debug_on = False
            else:
                self._is_debug_on = not self._is_debug_on
            if self._is_debug_on:
                return "Debug now on"
            else:
                return "Debug now off"
        else:
            # called as an unknown command handler
            if self._is_debug_on:
                cmd = args[2]
                arg = args[3]
                return u"Unknown command: '%s', args: [%s]" % (cmd, arg)

def Init(bot):
    cmd = 'debug'
    msd = MyStatefulDebug()
    return (cmd, msd, msd)

