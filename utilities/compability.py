# -*- coding: utf-8 -*-


def input(string):
    try:
        return raw_input(string)
    except NameError:
        # raw_input doesn't exist, assuming python 3+
        return input(string)
