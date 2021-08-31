import json
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


with open(os.path.join(__location__, "linkfeed.json"), "r") as fp:
    PRICE_FEED_ABI = json.loads(fp.read())
