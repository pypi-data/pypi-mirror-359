"""Module to provide interrupt-related interfaces and helper classes.

This is to support event-based programming techniques, also referred to
as publish-subscribe, asynchronous, event-driven behavior and so on.
The central interface is :class:`Interruptable`, which is meant to be
sub-classed by implementing devices. It can be registered with interrupt
handling routines and used to enable or disable interrupts on that device.

Upon an interrupt occurrence, the registered handler is called with an
:class:`.interruptable.Event` argument. It is intended to carry all
information available at no extra price in the moment of interrupt
occurrence. For that reason, it is likely to represent no more
information than just the fact, *that* an interrupt occurred. If a device
supports multiple INT lines, it can identify which one exactly caused
the interrupt.

All further information beyond that immediate response, especially if
requiring extra communication with the device, is considered to be event
context information and is represented by an :class:`EventContext` object.
This kind of data must be explicitly polled by the subscriber.
Whenever possible, that context polling should be done outside of the
handling routine as part of the response action.

:class:`EventContextControl` objects are used to control the order/priority
of context items while retrieving them from the device. 
"""
__author__ = "Oliver Maye"
__version__ = "0.1"
__all__ = ["Event", "EventContextControl", "EventContext", "Interruptable"]

import pymitter

from philander.systypes import ErrorCode


class Event():
    """Generic class to indicate the nature of an interrupt (source).
    
    Instances of this class are meant to be passed to the handling routine
    as an immediate response to interrupts. 
    """
    evtNone   = "EventNone"
    evtAny	  = "EventAny"
    evtInt1   = "EventInt1"
    evtInt2   = "EventInt2"


class EventContextControl():
    """Control data to navigate through the list of event context items.
    """
    clearAll    = 0
    getFirst    = 1
    getNext     = 2
    getLast     = 3
    getPrevious = 4

class EventContext:
    """Details or quantifies the reason for an interrupt occurrence.
    
    Will probably be sub-classed to represent specifics of the implementing
    :class:`Interruptable` device.
    """
    
    def __init__(self,
                 control: EventContextControl = EventContextControl.getFirst,
                 remainInt:  int = 0):
        self.control = control
        self.remainInt = remainInt

class Interruptable:
    """Generic interface to describe the capabilities of an event or interrupt source.
    
    This is an abstract base class to define common methods for enabling and
    disabling events as well as for managing event information of a specific
    device (implementation).
    """

    def __init__(self):
        self.eventEmitter = pymitter.EventEmitter()
        self.dictFeedbacks = dict()
            
    def registerInterruptHandler(self, onEvent=None, callerFeedBack=None, handler=None ):
        """Registers a handling routine for interrupt notification.
        
        The caller feedback will be directly passed to the handling routine.
        In case that multiple different interrupts are handled by the same
        routine, this parameter may be used to distinguish them and remember
        the source of interrupt.
        
        The handler should be a method or function that expects at least
        one argument. That first argument will be the ``callerFeedBack``
        object given as the above-mentioned parameter. Further parameters
        may follow, as they were handed in to the :meth:`_fire` method.
        The handler's signature should look like this:
        
        ``def handlingRoutine( feedback, *args) -> None:``
         
        Note that the ``onEvent`` parameter is *not* passed to the handler.
        It is eaten up by :meth:`_fire` and just controls the selection
        of the handling routine called.
        
        Depending on the parameter, this method behaves as follows:
        
        =================  =======  ============================================================
        onEvent            handler  semantics and action
        =================  =======  ============================================================
        Event.evtNone      None     All interrupts are disabled and all registrations cleared.
        Event.evtNone      valid    De-register the given handler from all events {Event.evtInt1|2|Any}.
        Event.evtInt1|2|*  None     De-register all handlers from the given event.
        Event.evtInt1|2|*  valid    Enable interrupt and register this handler for the given event.
        Event.evtAny       None     Clear the ``Event.evtAny`` registrations, only!
        Event.evtAny       valid    Register the handler for any event {Event.evtInt1|2}.
        =================  =======  ============================================================

        For this method, ``Event.evtNone`` is a semantic equivalent to
        ``None``.

        :param int onEvent: Exactly one of the event mnemonics defined\
        by the :class:`.interruptable.Event` enumeration.
        :param object callerFeedBack: Arbitrary object not evaluated\
        here, but passed on to the handler when an event is fired.
        :param handler: The handling routine to be called as an immediate\
        response to an event.
        :return: An error code indicating either success or the reason\
        of failure.
        :rtype: ErrorCode
        """
        ret = ErrorCode.errOk
        checkLastDisabled = False
        enableInt = False
        if (onEvent is None) or (onEvent == Event.evtNone):
            if (handler is None):   # Clear all registrations
                ret = self.disableInterrupt()
                self.eventEmitter.off_all()
                self.dictFeedbacks.clear()
            else:                   # De-register this handler from all events
                self.eventEmitter.off( Event.evtInt1, handler )
                if (len(self.eventEmitter.listeners(Event.evtInt1)) < 1) and \
                   (Event.evtInt1 in self.dictFeedbacks):
                    self.dictFeedbacks.pop( Event.evtInt1 )
                self.eventEmitter.off( Event.evtInt2, handler )
                if (len(self.eventEmitter.listeners(Event.evtInt2)) < 1) and \
                   (Event.evtInt2 in self.dictFeedbacks):
                    self.dictFeedbacks.pop( Event.evtInt2 )
                self.eventEmitter.off_any( handler )
                if (len(self.eventEmitter.listeners_any()) < 1) and \
                   (Event.evtAny in self.dictFeedbacks):
                    self.dictFeedbacks.pop( Event.evtAny )
                checkLastDisabled = True
        elif onEvent == Event.evtAny:
            if (handler is None):   # Clear 'any' registrations
                for f in self.eventEmitter.listeners_any():
                    self.eventEmitter.off_any( f )
                if onEvent in self.dictFeedbacks:
                    self.dictFeedbacks.pop( onEvent )
                checkLastDisabled = True
            else:                   # Register new handler for 'any' event
                self.eventEmitter.on_any( handler )
                self.dictFeedbacks[onEvent] = callerFeedBack
                enableInt = True
        else:
            if (handler is None):   # Clear all registrations for that event
                for f in self.eventEmitter.listeners(onEvent):
                    self.eventEmitter.off( onEvent, f )
                if onEvent in self.dictFeedbacks:
                    self.dictFeedbacks.pop( onEvent )
                checkLastDisabled = True
            else:                   # Register this handler for that event
                self.eventEmitter.on( onEvent, handler )
                self.dictFeedbacks[onEvent] = callerFeedBack
                enableInt = True
                
        if checkLastDisabled:     
            if (len(self.eventEmitter.listeners_all()) < 1):
                self.disableInterrupt()
                self.dictFeedbacks.clear()
        if enableInt:
            ret = self.enableInterrupt()
                
        return ret;

    def enableInterrupt(self):
        """Enables the interrupt(s) of the implementing device.

        :return: An error code indicating either success or the reason\
        of failure.
        :rtype: ErrorCode
        """
        return ErrorCode.errNotImplemented
    
    def disableInterrupt(self):
        """Disables the interrupt(s) of the implementing device.

        :return: An error code indicating either success or the reason\
        of failure.
        :rtype: ErrorCode
        """
        return ErrorCode.errNotImplemented
    
    def getEventContext(self, event, context):
        """After an event occurred, retrieves more detailed information\
        on the reason(s) for that interrupt.
        
        If a device supports more interrupt conditions than physical
        interrupt signalling lines, this is the way to find out, which
        of the condition(s) were met causing the last interrupt to _fire.
        For example, a temperature sensor could _fire its (one and only)
        interrupt line, if:
        * a high-temperature threshold is exceeded
        * a low-temperature threshold is undercut
        * the temperature didn't change (much) for some time interval
        * a new temperature measurement is available
        And some of these conditions could hold true simultaneously. Then,
        this function is to reveal more information on each single
        condition. E.g. the /new measurement available/ condition will
        deliver that new measurement data.
        
        That's why, it may be meaningful/necessary to call this method
        repeatedly, until all reasons were reported. Upon its first
        call after an event, the context's :attr:`.interruptable.EventContext.control`
        attribute must be set to :attr:`.interruptable.EventContextControl.getFirst`.
        Upon subsequent calls, this attribute should not be changed by
        the caller, anymore. In generally, event context information is
        retrieved in the order according to the priority of the
        corresponding event sources.
        
        The return value indicates, whether or not more information is
        available as follows:
        
        ==============================    ======================================================
        Return value                      Meaning
        ==============================    ======================================================
        :attr:`.ErrorCode.errOk`          Success. Last context info. No more data to retrieve.
        :attr:`.ErrorCode.errMoreData`    Success. Context is valid. More data to be retrieved.
        :attr:`.ErrorCode.errFewData`     No data to retrieve. Context is invalid.
        any other ErrorCode.*             Error. Context data is invalid.
        ==============================    ======================================================
        
        :param int event: The original event occurred, as recieved by the\
        handling routine. This must be one of the event mnemonics defined\
        by :class:``.interruptable.Event``.
        :param EventContext context: A representation of the context\
        information. The appropriate sub-class must be provided by the\
        device implementation. Upon the first call for each interrupt,\
        the ``control`` attribute must be set to either one of\
        ``evtCtxtCtrl_[clearAll | getFirst | getLast]``. In subsequent\
        calls, this attribute is updated automatically.\
        Upon return, this parameter contains the desired context information.
        :return: An error code indicating either success or the reason of failure.
        :rtype: ErrorCode
        """
        return ErrorCode.errNotImplemented
    
    def _fire(self, event, *args):
        """Raise an event.
        
        This is a helper method, meant to be used by derived classes,
        only.
        """
        if (event in self.dictFeedbacks):
            fb = self.dictFeedbacks[event]
        elif (not(event is None)) and (event != Event.evtNone) and (Event.evtAny in self.dictFeedbacks):
            fb = self.dictFeedbacks[Event.evtAny]
        else:
            fb = None
        if len(args) == 0:
            self.eventEmitter.emit( event, fb )
        else:
            self.eventEmitter.emit( event, fb, *args )
        return None