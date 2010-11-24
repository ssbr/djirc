#!/usr/bin/env python

# twisted imports
from twisted.internet import wxreactor
wxreactor.install()

# import twisted reactor *only after* installing wxreactor
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import sys
import platform
import os
import itertools

# third party
from lxml import etree

# local imports
from djirc import ui, eventtemplates

class IRCClient(irc.IRCClient):
    nickname = "testdjirc"
    password = None
    realname = None
    username = None
    userinfo = None
    fingerReply = None
    versionName = 'djirc'
    versionNum = '0.0a'
    versionEnv = platform.system()
    sourceURL = None
    lineRate = None
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.factory.view.receive_xml(etree.fromstring(
            self.factory.meta.view_event_templates['connect'].render()))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.factory.view.receive_xml(etree.fromstring(
            self.factory.meta.view_event_templates['disconnect'].render(
                msg=reason)))
    
    # callbacks for events
    
    def signedOn(self):
        """Called when client has succesfully signed on to server."""
        self.factory.view.receive_xml(etree.fromstring(
            self.factory.meta.view_event_templates['signon'].render()))
    
    def nickChanged(self, new_nick):
        """This will get called when the client's nickname has been changed."""
        # currently the behaviour is to display this in *all* windows
        # maybe it will be configurable later
        
        old_nick = self.nickname
        self.nickname = new_nick
        nick_msg = self.factory.meta.view_event_templates['you-change-nick'].render(
            old_nick=old_nick,
            new_nick=new_nick)
        
        for view in self.factory.views:
            view.receive_xml(etree.fromstring(nick_msg))
    
    def joined(self, channel):
        """This will get called when the client joins the channel."""
        ch = self.factory.views[channel] = self.factory.view.add_channel(channel)
        ch.receive_xml(etree.fromstring(
            self.factory.meta.view_event_templates['you-join'].render(
                channel=channel)))
    
    def _get_msg(self, user, channel, msg, event):
        """This will get called when the client receives a message, notice, or action"""
        nick = user.split('!', 1)[0]
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            try:
                target_view = self.factory.views[nick]
            except KeyError:
                target_view = self.factory.views[nick] = self.factory.view.add_convo(nick)
        else:
            target_view = self.factory.views[channel]
        
        target_view.receive_xml(etree.fromstring(
            self.factory.meta.view_event_templates[event].render(
                nick=nick,
                msg=msg)))
    
    def privmsg(self, user, channel, msg):
        """This will get called when the client receives a message."""
        self._get_msg(user, channel, msg, 'msg')
    
    def noticed(self, user, channel, msg):
        """This will get called when the client receives a notice."""
        self._get_msg(user, channel, msg, 'notice')
    
    def action(self, user, channel, msg):
        """This will get called when the client sees someone do an action."""
        self._get_msg(user, channel, msg, 'action')

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        if old_nick == self.nickname:
            self.nickChanged(new_nick)
        else:
            self.factory.view.receive_xml(etree.fromstring(
                self.factory.meta.view_event_templates['change-nick'].render(
                    old_nick=old_nick,
                    new_nick=new_nick)))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '_'
    
    # dispatch routines
    def do_say(self, channel, data):
        # simulate a privmsg with this content for consistency
        self.msg(channel, data)
        self.privmsg(self.nickname, channel, data)
    
    def do_me(self, channel, data):
        self.describe(channel, data)
        self.action(self.nickname, channel, data)
    
    def do_msg(self, _channel, data):
        user, data = data.split(' ', 1)
        
        self.msg(user, data)
        
        # simulate receiving message -- will also open new tab/view if needed
        self.privmsg(self.nickname, user, data)
    
    def do_join(self, _channel, data):
        self.join(data)
    
    def do_nick(self, _channel, data):
        self.setNick(data)
    
    
    
    
    
    def irc_unknown(self, *args, **kwargs):
        log.msg('Received unknown message: %s %s' % (args, kwargs))


class IRCClientFactory(protocol.ClientFactory):
    """A factory for IRC Clients.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = IRCClient
    
    def __init__(self, name, metaclient, view):
        self.name = name
        self.meta = metaclient
        self.view = view
        
        self.views = {'*': view} # * is for MotDs, at least in ircd7
    
    def buildProtocol(self, *args, **kwargs):
        proto = protocol.ClientFactory.buildProtocol(self, *args, **kwargs)
        self.protocol_instance = proto
        return proto
    
    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        # FIXME: should use templates
        # TODO: test this
        self.view.receive_xml(etree.fromstring(
            self.factory.meta.view_event_templates['disconnect'].render(
                msg=reason)))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        # FIXME: should use templates
        # TODO: test this
        self.view.receive_xml(etree.fromstring(
            self.factory.meta.view_event_templates['connect-failure'].render(
                msg=reason)))
    
    def send_command(self, irc_context, line):
        """Parse a command line and do relevant actions or send relevant data
        
        irc_context is the context in which the line was entered. It may be
        a channel name or nick.
        
        """
        if line.startswith('//'): # xchat behavior
            command = 'say'
            data = line[1:]
        elif line.startswith('/'):
            command, data = line[1:].split(' ', 1)
        else:
            command = 'say'
            data = line
        
        data = data.encode('utf-8')
        try:
            dispatched = getattr(
                self.protocol_instance,
                'do_%s' % command)
        except AttributeError:
            self.view.receive_xml(etree.fromstring(elf.factory.meta.
                view_event_templates['invalid-command'].render(
                    input=command)))
        else:
            if irc_context is not None:
                dispatched(irc_context, data)
            else:
                if command in ['say', 'me', 'notice']:
                    self.view.receive_xml(etree.fromstring(self.factory.meta.
                        view_event_templates['need-channel-context'].render(
                            input=command)))
                else:
                    dispatched(None, data)

class IRCMetaClient(object):
    """This is the multi-network client handling individual network connections
    
    contains multiple IRCClientFactories, one for each network connection,
    and manages the relationship with the UI (where it isn't passed off to the
    protocol or factory).
    
    """
    def __init__(self, reactor, ui):
        """Create IRCMetaClient using `reactor` and IUserInterface `ui`"""
        self.reactor = reactor
        self.ui = ui
    
    def connect_to_network(self, name, port):
        network_view = self.ui.add_network(name)
        factory = IRCClientFactory(name, self, network_view)
        # FIXME: HACK HACK HACK
        #        won't work for multiple servers
        self.ui.factory = factory
        # END HACK
        self.reactor.connectTCP(name, port, factory)

def main():
    # initialize logging
    ##log.startLogging(sys.stdout)
    ui_name = 'wx'
    __import__('djirc.ui.%s' % ui_name)
    ui_module = getattr(ui, ui_name)
    
    
    # create GUI
    metaclient = ui_module.create_metaclient(reactor, IRCMetaClient)
    pth = os.path.join(os.path.dirname(__file__), 'data', 'event_templates.yaml')
    with open(pth) as f:
        metaclient.view_event_templates = eventtemplates.JinjaTemplateDict.from_yaml_f(f)
    
    metaclient.connect_to_network("irc.freenode.net", 6667)
    

    # run bot
    reactor.run()
