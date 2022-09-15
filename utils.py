"""
Name:    utils.py
Author:  kyh
Created: 9/11/2022 10:52 PM
"""
import datetime
import functools
import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


@functools.cache
def today():
    return datetime.date.today()


if __name__ == "__main__":
    pass
