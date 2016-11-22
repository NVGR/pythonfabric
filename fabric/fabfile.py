from fabric.api import *


def hello(name='World!', greeting='How r u?'):
    print 'Hello {0}, {1}'.format(name, greeting)