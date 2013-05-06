#!/usr/bin/env python
# -*- coding: utf-8 -*-


class LargeScaleException(Exception):
    def __init__(self, message, Errors=None):
        Exception.__init__(self, message)

        self.Errors = Errors


class LoggingException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class ArgParseException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class GeneratorException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class EmulatorException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class ConfiguratorException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class ScriptException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class InterfaceNotFoundException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class LinkNotFoundException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class ContainerNotFoundException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class CleanupException(EmulatorException):
    def __init__(self, message, Errors=None):
        EmulatorException.__init__(self, message, Errors)


class SSHLinkException(EmulatorException):
    def __init__(self, message, Errors=None):
        EmulatorException.__init__(self, message, Errors)


class BridgeNotFoundException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class ComponentException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class NoFreeInterfacesException(ComponentException):
    def __init__(self, message, Errors=None):
        ComponentException.__init__(self, message, Errors)


class IPComponentException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class InsufficientRightsException(LargeScaleException):
    def __init__(self, message, Errors=None):
        LargeScaleException.__init__(self, message, Errors)


class IncorrectArgumentsException(EmulatorException):
    def __init__(self, message, Errors=None):
        EmulatorException.__init__(self, message, Errors)
