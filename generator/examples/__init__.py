#!/usr/bin/env python
# -*- coding: utf-8 -*-

#__all__ = ["citybus", "cityflow", "cityring", "citystar", "smalltop"]

import os
import glob
__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]

