#! /usr/bin/python2
# -*- coding: utf-8 -*-

# Chibi Modular Bot
# Copyright (C) 2012 FSi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



from jabberbot import botcmd
from muc import MUCJabberBot
import os
import json
import re
import glob
import codecs
import inspect
import importlib

class ChmobotBadConfigError(Exception): pass

class ChmobotJabberBot(MUCJabberBot):
    """Chmobot Jabber bot"""
    # dictionary for configuration
    cfg = {}
    __command_prefix = ''
    # list of modules
    _modules = []
    # list of handlers
    _handlers = []
    
    def __init__(self, *args, **kwargs):
        # looking if command_prefix is supplied
        if len(args)==8:
            self.__command_prefix = args[7]
        if "command_prefix" in kwargs:
            self.__command_prefix = kwargs["command_prefix"]
        # call parent's __init__
        super(ChmobotJabberBot, self).__init__(*args, **kwargs)
    
    def set_config(self, c_dict):
        # updating cfg
        self.cfg = c_dict
        # loading default modules (if any)
        if "modules" in self.cfg:
            amod = self._available_modules()
            for mod in self.cfg["modules"]:
                if mod in amod:
                    try:
                        self._load_module(mod)
                    except ImportError as ie:
                        self.log.warn("There was a problem loading module %s: %s" %
                            (mod, ie.message))
                        self.cfg["modules"].remove(mod)
                    else:
                        self.log.info("Loaded module %s" % mod)
                else:
                    self.cfg["modules"].remove(mod)


    # ====================================================
    # utility
    def _save_conf(self):
        """Saves the config file"""
        try:
            c_file = codecs.open('chmobot.conf', 'w', encoding='utf-8')
            json.dump(self.cfg, c_file, indent=4, ensure_ascii=False)
        finally:
            c_file.close()
            
    def _available_modules(self):
        """Returns a list of available modules"""
        return [os.path.splitext(os.path.basename(f_name))[0] # <-- module's filename without extension
            for f_name in glob.glob("plugins/*.py")]

    def _load_module(self, module_name):
        """Tries to load module from specified file"""
        try:
            # 1. import the module file
            mod = importlib.import_module("plugins." + module_name)
            # 2. force recompilation
            reload(mod)
            # 3. save module reference for safekeeping
            if mod not in self._modules:
                self._modules.append(mod)
        #except ImportError as ie:
            #raise ImportError("Couldn't load %s" % module_name)
        except Exception as e:
            raise ImportError("Couldn't load %s:\n%s" % (module_name, e.args))
        else:
            # 3. add command that the module defines
            #   call %module.Init() and append result to the _handlers list
            try:
                self._handlers.append(mod.Init(self))
            except Exception as e:
                raise ImportError("Couldn't init module %s\n%s" % (module_name, e.args))
            
    def _remove_module(self, module_name):
        """Tries to remove specified module"""
        # retrieve module by its name
        mod = [m for m in self._modules if m.__name__ == "plugins." + module_name]
        if len(mod): mod = mod[0]
        # remove the commands this module added
        cmd = mod.Init()[0]
        handler_list = filter(lambda t: t[0] == cmd, self._handlers)
        for h in handler_list:
            self._handlers.remove(h)
        # and finally, remove the module
        self._modules.remove(mod)
    
    
    # ====================================================
    # callbacks
    def unknown_command(self, mess, cmd, args):
        """Unknown command callback"""
        # check if cmd starts with __command_prefix
        if cmd.startswith(self.__command_prefix):
            # check if it's actually a known command
            print len(self._handlers)
            for (command, handler, uh) in self._handlers:
                # this ------------v  cuts off the __command_prefix part
                if (command == cmd[len(self.__command_prefix):]):
                    return handler(self, mess, args)
        # next, try all modules' unknown command handlers
        for (command, handler, uh) in self._handlers:
            # the first successful unknown_command handler gets the bird!
            if uh and uh(self, mess, cmd, args):
                return uh(self, mess, cmd, args)
        # couldn't handle, return None
        return None
    
    def shutdown(self):
        """shutdown callback"""
        try:
            self._save_conf()
        except:
            # couldn't save. make an OKAYFACE and die.
            pass
    
    @botcmd
    def help(self, mess, args):
        # this help function can query available plugins
        # 1. if user asked for generic help:
        if not args:
            pass
            # 1.1. get help message from the superclass
            try:
                top = super(ChmobotJabberBot, self).help(mess, args)
            except Exception as e:
                top = e.message
            # 1.2. get list of plugin commands
            usage = '\n\nPlugin commands:\n\n' + '\n'.join(sorted([
               '%%%s: %s' % (cmd,
                   (handler.__doc__ or '(undocumented)').strip().split('\n', 1)[0])
               for (cmd, handler, uh) in self._handlers \
               if cmd]))
        else:
            top = ''
            usage = 'hui'
            cmds = {self.__command_prefix + cmd: handler.__doc__ for (cmd, handler, uh) in self._handlers}
            #usage = '\n'.join(["%s - %s" % (a, b) for (a, b) in cmds.items()])
            if (args not in cmds and 
               (self.__command_prefix + args) in cmds):
               # automatically add prefix if missing
               args = self.__command_prefix + args
            if args in cmds:
                top = args + ' :\n\n'
                usage = cmds[args] or '(undocumented)'
            else:
                top = ''
                # else get help message from the superclass
                usage = super(ChmobotJabberBot, self).help(mess, args)
        return top + usage
            

    # ====================================================
    # some default commands
    @botcmd(hidden=True)
    def modprobe(self, mess, args):
        """Tries loading the specified module. Owner only."""
        jid = mess.getFrom().getStripped()
        module = args.split()[0]
        if jid in self.cfg['ownerjids']:
            if not self.cfg['modules']:
                self.cfg["modules"] = []
            if module not in self.cfg["modules"]:
                try:
                    self._load_module(module)
                except ImportError as ie:
                    return "There was a problem: %s" % ie.message
                else:
                    self.cfg["modules"].append(module)
                    return "Done."
        else:
            return "Access denied."
    
    @botcmd(hidden=True)
    def rmmod(self, mess, args):
        """Unloads specified module"""
        jid = mess.getFrom().getStripped()
        module = args
        if jid in self.cfg["ownerjids"]:
            if module in self.cfg["modules"]:
                try:
                    self._remove_module(module)
                    self.cfg["modules"].remove(module)
                except Exception as e:
                    return u"There was a problem: %s" % e.args
                else:
                    return "Done."
            else:
                return "Not loaded."
        else:
            return "Access denied."
            
    @botcmd(hidden=True)
    def savecfg(self, mess, args):
        """Saves config in JSON format"""
        jid = mess.getFrom().getStripped()
        if jid in self.cfg["ownerjids"]:
            self._save_conf()
        else:
            return "Access denied."
    
    @botcmd
    def lsmod(self, mess, args):
        """Lists loaded modules"""
        return "Loaded modules: " + ' '.join(self.cfg["modules"])
    
    @botcmd(hidden=True)
    def mucjoin(self, mess, args):
        """Joins specified MUC"""
        jid = mess.getFrom().getStripped()
        conference = args.split()[0]
        nickname = self.cfg['nickname']
        if jid in self.cfg['ownerjids']:
            # joining
            self.join_room(conference, nickname)
            # saving conference in cfg to join it next time
            if not self.cfg['conferences']:
                self.cfg['conferences'] = []
            self.cfg['conferences'].append(conference)
            return "Joined %s." % conference
        else:
            return "Access denied."

    @botcmd(hidden=True)
    def restart(self, mess, args):
        """Restarts the bot"""
        jid = mess.getFrom().getStripped()
        if jid in self.cfg['ownerjids']:
            self.quit()
        else: 
            return "Access denied."






if __name__ == '__main__':
    c_file = codecs.open('chmobot.conf', 'r', encoding='utf-8')
    cfg = json.loads(c_file.read())
    c_file.close()

    # mandatory parameters
    try:
        username = cfg['username']  # if no such key, halting is ok
        password = cfg['password']  # if no such key, halting is ok
    except KeyError:
        raise ChmobotBadConfigError('')
    # optional parameters
    resource = ('resource' in cfg) and cfg['resource'] or u'Чмо'
    conferences = ('conferences' in cfg) and cfg['conferences'] or None
    nickname = ('nickname' in cfg) and cfg['nickname'] or u'Чмо'
    
    bot = ChmobotJabberBot(cfg['username'], cfg['password'], res=resource, debug=True, command_prefix='%')
    bot.set_config(cfg)
    if(conferences):
        for conference in conferences:
            bot.join_room(conference, nickname)
    bot.serve_forever()
