import datetime
import os
import random
import time
from binascii import hexlify

START_TIME = int(datetime.datetime(year=2019, month=6, day=22, hour=2, minute=35, second=49).timestamp())


def create_hash():
    return str(hexlify(os.urandom(16)), 'ascii')


def time_stamp():
    return int(round(time.time()))


def make_id():
    """
    Inspired by http://instagram-engineering.tumblr.com/post/10853187575/sharding-ids-at-instagram
    https://stackoverflow.com/questions/37558821/how-to-replace-djangos-primary-key-with-a-different-integer-that-is-unique-for
    """
    t = int(time.time() * 1000) - START_TIME
    u = random.SystemRandom().getrandbits(23)
    id_ = (t << 23) | u
    return id_


def reverse_id(id_):
    t = id_ >> 23
    return t + START_TIME
