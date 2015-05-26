import urllib
import urllib2
import json
import inspect
import logging
import math
import time
import pickle

class CAPCHAException(Exception):
    def __init__(self, cid, url):
        self.cid = cid
        self.url = url

class AccessError(Exception):
    pass

class UserDB(object):

    jobs = ['wall', 'friend', 'private']

    def __init__(self, filename, new=False, read_only=False):
        self.filename = filename
        self.read_only = read_only
        if not new:
            d = pickle.load(file(self.filename))
            self.users = d['users']
            self.tokens = d['tokens']
            self.logs = d['logs']
        else:
            self.users = {}
            self.tokens = {}
            self.logs = []
        self._load_logs()

    def __del__(self):
        self._sync()

    def _sync(self):
        """ save all changes on disk """
        if not self.read_only:
            d = {}
            d['users'] = self.users
            d['tokens'] = self.tokens
            d['logs'] = self.logs
            pickle.dump(d, file(self.filename, "w"))

    def _load_logs(self):
        bad = set()
        wall = set()
        private = set()
        friend = set()

        for user in self.users.values():
            if 'deactivated' in user:
                bad.add(user['uid'])
            elif user['can_post'] == 1:
                wall.add(user['uid'])
            elif user['can_write_private_message'] == 1:
                private.add(user['uid'])
            else:
                friend.add(user['uid'])

        log_wall = set()
        log_private = set()
        log_friend = set()
        for (uid, token_id, message_type) in self.logs:
            if message_type == 'wall':
                log_wall.add(uid)
            elif message_type == 'private':
                log_private.add(uid)
            elif message_type == 'friend':
                log_friend.add(uid)

        logging.info("Loaded processed_users w/p/f:%d %d %d" % (len(log_wall), len(log_private), len(log_friend)))

        self.wall = list(wall-log_wall) 
        self.private = list(private-log_private) 
        self.friend = list(friend-log_friend) 

        logging.info("Remained users %d %d %d" % (len(self.wall), len(self.private), len(self.friend)))

    def add_token(self, token, uid, comment):
        """ add new token to db """
        self.tokens[token] = {}
        for j in self.jobs:
            self.tokens[token][j] = 0
            self.tokens[token]["%s_counter" % j] = 0
        try:
            self.tokens[token]['id'] = max([t['id'] for t in self.tokens.values()])+1
        except KeyError:
            self.tokens[token]['id'] = 0
        except ValueError:
            self.tokens[token]['id'] = 0
        self.tokens[token]['uid'] = uid
        self.tokens[token]['comment'] = comment

    def get_token(self, job_type):
        """ job_type: ['wall', 'friend', 'private'] """
        for t in self.tokens:
            if self.tokens[t][job_type] == 0:
                self.tokens[t][job_type] = 1
                return t

    def get_token_id(self, token):
        """ return: token_id """
        if token in self.tokens:
            return self.tokens[token]['id']

    def get_proxy(self, token):
        """ return the same proxy for the same token """
        pass

    def get_friend(self):
        r = self.friend[:50]
        self.friend = self.friend[50:]
        return r

    def get_wall(self):
        r = self.wall[:40]
        self.wall = self.wall[40:]
        return r

    def get_private(self):
        r = self.private[:20]
        self.private = self.private[20:]
        return r

    def log(self, uid, token, message_type):
        """ uid - user id
            token - for done job
            message_type: ['wall', 'friend', 'private', 'error']
        """
        self.logs.append((uid, self.get_token_id(token), message_type, ))

class VKAPISession(object):

    def __init__(self, token):
        self.token = token

        self.last_request = time.time()

        self.raw_api = VKAPISession.api(self)
        self.friends = VKAPISession.friends(self)
        self.users = VKAPISession.users(self)
        self.wall = VKAPISession.wall(self)
        self.messages = VKAPISession.messages(self)
        self.groups = VKAPISession.groups(self)
        self.database = VKAPISession.database(self)

    class api(object):

        api_host = "https://api.vk.com/method/%s?%s"

        def __init__(self, session):
            self.session = session

        def _call(self, method, args, delay=2):
            logging.debug("[api] %s(%s)", method, args)
            args.append(("access_token", self.session.token))

            if time.time() - self.session.last_request < 0.3:
                time.sleep(0.3)

            r  = json.loads(urllib2.urlopen(self.api_host % (method, urllib.urlencode(args))).read())
            if "error" in r:
                if 'captcha_sid' in r['error']:
                    raise CAPCHAException(r['error']['captcha_sid'], r['error']['captcha_img'])
                elif r['error']['error_code']==7:
                    raise AccessError()
                elif r['error']['error_code']==6:
                    logging.info("[api] too fast. sleeping for %d seconds" % int(2*math.log(delay, 2)))
                    time.sleep(2*math.log(delay, 2))
                    return self._call(method, args, delay+1)
                elif r["error"]['error_code']==214:
                    raise AccessError(r["error"]['error_msg'])
                raise Exception("API Error:" + str(r))
            return r["response"]

    def execute(self, code):
        args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
        return self.raw_api._call("execute", args)

    class friends(api):

        def get(self, uid=None, fields=None, name_case=None, count=None, offset=None, lid=None, order=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

        def add(self, uid, text=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

    class users(api):

        def get(self, uids, fields=None, name_case=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

        def search(self, q, fields=None, count=1000, offset=0, city=None, country=None, hometown=None, 
                   university_country=None, university=None, university_year=None, university_faculty=None,
                   university_chair=None, sex=None, status=None, age_from=None, age_to=None,
                   birth_day=None, birth_month=None, birth_year=None,
                   ):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

    class wall(api):

        def post(self, owner_id=None, message=None, attachments=None, lat=None,
                 long=None, place_id=None, services=None, from_group=None,
                 signed=None, friends_only=None,
                 captcha_sid=None, captcha_key=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

    class messages(api):

        def send(self, uid=None, message=None, attachment=None, forward_messages=None,
                 title=None, type=None, lat=None, long=None, guid=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

    class groups(api):

        def getMembers(self, gid, count=None, offset=None, sort=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

        def getAllMembers(self, gid):
            r = self.getMembers(gid)
            count = r['count']
            users = r['users']
            off = 1
            while len(users) < count:
                r = self.getMembers(gid, offset=off*1000)
                users.extend(r['users'])
                off += 1
                logging.debug("process groups: gid:%d off:%d, processed_users:%d", gid, off, len(users))
            return users

    class database(api):

        def getCountries(self, need_all=None, code=None, offset=None, count=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

        def getCities(self, country_id=1, region_id=None, q=None, need_all=None, offset=None, count=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)

        def getUniversities(self, q=None, country_id=1, city_id=None, offset=None, count=None):
            args = [(arg_name, arg) for (arg_name, arg) in locals().items() if arg_name!='self' and arg]
            return self._call("%s.%s" % (self.__class__.__name__, inspect.stack()[0][3]), args)
