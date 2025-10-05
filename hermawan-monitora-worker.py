import argparse
import logging
import schedule
from datetime import datetime

from conf import conf
from const import DEFAULT_ENV_FILEPATH
from db.redis import hmon_redis
from task.ports_scan import ports_scan


def task_ports_scan():
    global running
    if not running:
        running = True
        if logging.root.level == 10:
            start = datetime.now()
        ports_scan.get_instance().main()
        if logging.root.level == 10:
            end = datetime.now()
            td = (end - start).total_seconds()
            logging.debug("Duration {} Seconds".format(td))
        running = False


if __name__ == "__main__":
    # Get Command Line Arguments
    parser = argparse.ArgumentParser(
      description="""Hermawan-Monitora is a monitoring application, \
and the main feature is for monitoring services' health.
This is the worker service.
For more description and help please check:
https://github.com/ming-hermawan/hermawan-monitora-manual/blob/master\
/hemawan-monitora-manual.pdf"""
    )
    parser.add_argument(
      "--env", default=DEFAULT_ENV_FILEPATH,
      help="env file path")
    args = parser.parse_args()

    # Initialization
    conf_obj = conf.get_instance(args.env)
    logging.basicConfig(level=conf_obj.get_log_lvl())
    interval = int(conf_obj.get_interval())
    redis_obj = hmon_redis()
    redis_obj.set_ports_scan_status('INIT')
    global running
    running = False

    # Run
    schedule.every(interval).seconds.do(task_ports_scan)
    while True:
        schedule.run_pending()
