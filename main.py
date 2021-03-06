# #!/usr/bin/env python3.6
import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import tornado.web

from abuse_checker import AbuseChecker
from cds import CdsRequest
from data_processors import WebDataProcessor
from data_providers import get_data_provider
from data_types import AbuseRule
from tgbot import BusBot
from tracking import EventTracker, WebEvent
from website import BusSite

if not Path('logs').is_dir():
    Path('logs').mkdir()

# Enable logging
file_handler = TimedRotatingFileHandler("logs/vrnbus.log", 'midnight', 1)
file_handler.suffix = "%Y-%m-%d"
# noinspection SpellCheckingInspection
logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(levelname)s [%(filename)s:%(lineno)s %(funcName)10s] %(message)s',
                    datefmt="%H:%M:%S",
                    level=logging.INFO,
                    handlers=[logging.StreamHandler(), file_handler])

logger = logging.getLogger("vrnbus")

logger.info([{k: os.environ[k]} for (k) in os.environ if 'PATH' not in k])

user_settings = {}

if __name__ == "__main__":
    tracker = EventTracker(logger)
    abuse_rules = [
        AbuseRule(WebEvent.BUSMAP, 5, datetime.timedelta(minutes=90)),
        AbuseRule(WebEvent.BUSINFO, 10, datetime.timedelta(minutes=60)),
    ]

    anti_abuser = AbuseChecker(logger, abuse_rules)
    data_provider = get_data_provider(logger)
    cds = CdsRequest(logger, data_provider)
    data_processor = WebDataProcessor(cds, logger)
    bot = BusBot(cds, user_settings, logger, tracker)
    application = BusSite(data_processor, logger, tracker, anti_abuser)
    application.listen(os.environ.get('PORT', 8080))
    tornado.ioloop.IOLoop.instance().start()
