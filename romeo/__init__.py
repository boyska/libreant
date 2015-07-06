'''
Oh Romeo, why are you, Romeo?

whois is for authentication: checking which user you belong to.
It can accept not only user/pass, but also other kind of data, allowing
multiple way of authenticating; for example, REMOTE_USER could be used.

canihaz is for checking permissions. Permissions work this way:
    - a "capability" is the permission of doing a specific thing. It should be
    finegrained, but of course that's up to you
    - a "role" is a regexp on capabilities. Of course a regexp could just be a
    list of capabilities in or, but wildcard are allowed, yay!
    - a "user" has many roles
'''
from __future__ import print_function
import re
from collections import defaultdict
from functools import wraps


class HtpasswdWhoisBackend(object):
    def __init__(self, fpath):
        from passlib.apache import HtpasswdFile
        self.htpass = HtpasswdFile(fpath)

    def check(self, auth_data):
        '''we only care about auth_data['user'] and auth_data['password']'''
        if 'user' not in auth_data or 'password' not in auth_data:
            return None
        user = auth_data['user']
        password = auth_data['password']
        if self.htpass.check_password(user, password):
            return user
        return None


class RemoteuserWhoisBackend(object):
    def __init__(self, limit_function=None):
        self.limit = limit_function

    def check(self, auth_data):
        return auth_data.get('remote_user', None)


class Authenticator(object):
    def __init__(self, authentication_backends, userrole_fpath, roledef_fpath,
                 auth_data_getter):
        self.authenticators = authentication_backends
        self.user_roles = defaultdict(list)
        if userrole_fpath is not None:
            with open(userrole_fpath) as buf:
                for line in buf:
                    user, groups = line.split(':', 1)
                    self.user_roles[user].extend(groups.split())

        self.roledef = {}
        if roledef_fpath is not None:
            with open(roledef_fpath) as buf:
                for line in buf:
                    role, regexp = line.split(':', 1)
                    self.roledef[role] = re.compile(regexp[:-1])
        self.auth_data_getter = auth_data_getter

    def whois(self, auth_data):
        for authbe in self.authenticators:
            res = authbe.check(auth_data)
            if res is not None:
                print('sei', res)
                return res
        print('sei anon')
        return '_anonymous'

    def canihaz(self, user, capability):
        for r in self.user_roles[user]:
            if r in self.roledef and \
                    self.roledef[r].match(capability) is not None:
                return True
            print(self.roledef.get(r).pattern)
        return False

    def requires_capability(self, capability):
        def decorator(function):
            @wraps(function)
            def decorated(*args, **kwargs):
                if not self.canihaz(self.whois(self.auth_data_getter()),
                                    capability):
                    raise CapabilityMissingException(capability)
                return function(*args, **kwargs)
            return decorated
        return decorator


class CapabilityMissingException(Exception):
    def __init__(self, cap_name):
        Exception.__init__(self, cap_name)
