#!/usr/bin/env python
# -*- coding: utf-8 -*-

class TopologyException(Exception) :
    def __init__(self, message, Errors) :
        Exception.__init__(self, message)

        self.Errors = Errors


class InterfaceNotFoundException(Exception) :
    def __init__(self, message, Errors) :
        TopologyException.__init__(self, message, Errors)


class LinkNotFoundException(Exception) :
    def __init__(self, message, Errors) :
        TopologyException.__init__(self, message, Errors)


class ContainerNotFoundException(Exception) :
    def __init__(self, message, Errors) :
        TopologyException.__init__(self, message, Errors)


class BridgeNotFoundException(Exception) :
    def __init__(self, message, Errors) :
        TopologyException.__init__(self, message, Errors)


class ComponentException(Exception) :
    def __init__(self, message, Errors) :
        TopologyException.__init__(self, message, Errors)


class NoFreeInterfacesException(Exception) :
    def __init__(self, message, Errors) :
        ComponentException.__init__(self, message, Errors)


class IPComponentException(Exception) :
    def __init__(self, message, Errors) :
        TopologyException.__init__(self, message, Errors)


class InsufficientRightsException(Exception) :
    def __init__(self, message, Errors) :
        TopologyException.__init__(self, message, Errors)
