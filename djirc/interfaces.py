#!/usr/bin/env python
"""This module currently represents things as they are headed in the future.

Where it is out of sync with reality, reality is wrong and will be corrected.

"""

from zope.interface import Interface, Attribute

class IUserInterface(Interface):
    def add_network(name):
        """Add networked named `name` to the UI
        
        returns an IUINetwork
        
        """
    

class IUIWindow(Interface):
    """Handle for the UI's main window as used in the window manager"""
    def highlight():
        """Highlight the UI in the window manager (e.g. flash tab in taskbar)
        
        May be unimplemented
        
        """
    
    def unhighlight():
        """Remove any highlight on the UI
        
        May be unimplemented. Does not raise an error if the UI was not
        highlighted.
        
        """
    
    def set_window_title(title):
        """Set the window manager title to `title`
        
        May be unimplemented
        
        """
    
    def get_window_title(title):
        """Get the window manager title as it is now
        
        May not necessarily reflect changes made yet. It's inadvisable to use this
        for anything serious.
        
        May be unimplemented.
        
        """
    
    def create_notification(title, contents):
        """Create notification dialog.
        
        XXX: INTERFACE MAY CHANGE, SEMANTICS UNKNOWN
        
        May be unimplemented.
        
        """
    
    def focus():
        """Bring window to top of window stack
        
        May be unimplemented. Some WMs don't even have window stacks!
        
        """

class IUITab(Interface):
    def highlight():
        """Highlight the tab view in the UI
        
        May be unimplemented
        
        """
    
    def unhighlight():
        """Remove any highlight on the tab view in the UI
        
        May be unimplemented. Does not raise an error if the view was not
        highlighted.
        
        """
    
    def close():
        """Close tab display.
        
        Any future attempts to write will raise a ValueError
        
        """
    
    def receive_xml(data):
        """Display line of XHTML-formatted text `data` in the tab
        
        """

class IUINetwork(Interface):
    """Handle for the UI's network tree/tab
    
    if the UI doesn't have such a thing, many visual methods may be no-ops --
    but others cannot be (such as add_channel)
    
    """
    
    def add_channel(channel_name):
        """Add channel named `channel_name` to the UI for this network
        
        returns an IUIChannel
        
        """
    
    def add_convo(nick):
        """Add convo with `nick` to the UI for this network
        
        returns an IUIConvo
        
        """

class IUIChannel(IUITab):
    """Handle for the UI's channel tab/display
    
    the UI may not have an isolated display, but nonetheless must pretend to
    for the purposes of this interface.
    
    """
    
    def set_topic(topic):
        """Change the Channel UI to display a new topic, `topic`."""
    
    

class IUIUserList(Interface):
    """Handle for a channel tab user-list.
    
    Presently just accepts user set management. Actual sorting/etc. is left to
    the UI implementation
    
    """
    def add_user(nick):
        """Add `nick` to the user list"""
    
    def remove_user(nick):
        """Add `nick` to the user list"""

class IUIConvo(IUITab):
    """Handle for the UI's private conversation tab/display
    
    the UI may not have an isolated display, but nonetheless must pretend to
    for the purposes of this interface.
    
    """
    
