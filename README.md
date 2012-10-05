chmobot v0.1.0
==============

Chibi Modular bot: Simplistic XMPP MUC bot built on top of XMPPpy and jabberbot.py


Prerequisites
-------------
You will need to install two packages:
1. xmpppy (http://xmpppy.sourceforge.net/)
2. jabberbot.py (http://thp.io/2007/python-jabberbot/)
   copy muc.py from examples/ folder of python-jabberbot if necessary


Installation
------------
Unpack, edit chmobot.conf and hopefully it'll start.


Config file format
------------------
chmobot.conf is a file in JSON format. An example of this is included in the distribution.

Main parameters:
    * username: XMPP account for the bot
    * password: credentials for said XMPP account
    * resource: bot's XMPP resource

    * ownerjids: a list of JIDs of trusted users (who can add and remove modules, restart bot etc.) 
    * modules: a list of modules to load on startup

    * conferences: a list of conferences to join on startup
    * nickname: nickname to use in conferences

Plugin format
-------------
