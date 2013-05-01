#!/usr/bin/env python
# -*- coding: utf-8 -*-

class LargeScaleException(Exception) :
    def __init__(self, message, Errors = None) :
        Exception.__init__(self, message)

        self.Errors = Errors

class InterfaceNotFoundException(LargeScaleException) :
    def __init__(self, message, Errors = None) :
        LargeScaleException.__init__(self, message, Errors)


class LinkNotFoundException(LargeScaleException) :
    def __init__(self, message, Errors = None) :
        LargeScaleException.__init__(self, message, Errors)


class ContainerNotFoundException(LargeScaleException) :
    def __init__(self, message, Errors = None) :
        LargeScaleException.__init__(self, message, Errors)


class BridgeNotFoundException(LargeScaleException) :
    def __init__(self, message, Errors = None) :
        LargeScaleException.__init__(self, message, Errors)


class ComponentException(LargeScaleException) :
    def __init__(self, message, Errors = None) :
        LargeScaleException.__init__(self, message, Errors)


class NoFreeInterfacesException(ComponentException) :
    def __init__(self, message, Errors = None) :
        ComponentException.__init__(self, message, Errors)


class IPComponentException(LargeScaleException) :
    def __init__(self, message, Errors = None) :
        LargeScaleException.__init__(self, message, Errors)


class InsufficientRightsException(LargeScaleException) :
    def __init__(self, message, Errors = None) :
        LargeScaleException.__init__(self, message, Errors)


class IncorrectArgumentsException(LargeScaleException) :
    def __init__(self, message, Errors = None) :
        LargeScaleException.__init__(self, message, Errors)
