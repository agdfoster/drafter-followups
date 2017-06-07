from talon import signature
from talon.quotations import register_xpath_extensions


def init():
    register_xpath_extensions()
    signature.initialize()
