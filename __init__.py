# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import hooks


def post_init_hook(env):
    hooks.post_init_hook(env)
