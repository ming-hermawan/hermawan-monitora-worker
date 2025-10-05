import nmap
import os
import logging
from datetime import datetime

from conf import conf
from db.sqlite.data import data
from db.redis import hmon_redis


class ports_scan:

    __instance = None

    @staticmethod
    def get_instance():
        if ports_scan.__instance is None:
            ports_scan()
        return ports_scan.__instance

    def __init__(self):
        if ports_scan.__instance is not None:
            raise Exception(
              'This class is a singleton, \
use ports_scan.get_instance() instead!'
            )
        else:
            self.__proc_init()
            ports_scan.__instance = self

    def __proc_init(self):
        conf_obj = conf.get_instance()
        self.__log_path = conf_obj.get_log_path()
        self.__port_scanner_obj = nmap.PortScanner()
        self.__redis_obj = hmon_redis()
        self.__write_to_file = conf_obj.write_to_file()

    def __publish_port_scan_result(self,
                                   ip: str,
                                   port: int,
                                   status: str):
        self.__redis_obj.publish_port_scan_result(
          ip,
          port,
          status)

    def __scan_port(self,
                    ip: str,
                    port: str,
                    datetime_now: datetime) -> str:
        if self.__write_to_file:
            start = datetime.now()
        res = self.__port_scanner_obj.scan(
          ip,
          str(port),
          arguments='--open -Pn')
        if self.__write_to_file:
            end = datetime.now()
            td = (end - start).total_seconds()
            filepath = "{0}/{1}_{2}.log".format(
              self.__log_path,
              ip.replace(".", "_", port),
              port)
            with open(filepath, mode='a') as o_file:
                o_file.write("{0}|{1}|{2}{3}".format(
                  datetime_now.strftime("%Y-%m-%d %H:%M:%S"),
                  td,
                  res,
                  os.linesep)
                )
                o_file.close()
        try:
            state = res['scan'][ip]['tcp'][port]['state']
            status = 'UP' if state == 'open' else 'DOWN'
        except KeyError:
            status = 'DOWN'
        if self.__last_status[ip][port] == status:
            pass
        else:
            self.__last_status[ip][port] = status
            self.__publish_port_scan_result(
              ip,
              port,
              status)
        return status

    def main(self):
        self.__last_status = {}
        status = self.__redis_obj.get_ports_scan_status()
        logging.debug("REDIS status = {}".format(status))
        obj_data = data()
        if status == 'INIT':
            self.temp = obj_data.get_data_ip_ports()
            self.__redis_obj.set_ports_scan_status('SCAN')
            status = 'SCAN'
        if status == 'SCAN':
            datetime_now = datetime.now()
            for x in self.temp:
                ip = x[1]
                port = x[3]
                self.__last_status[ip] = {port: None}
                port_status = self.__scan_port(
                  ip=ip,
                  port=port,
                  datetime_now=datetime_now)
                self.__redis_obj.set_last_ports_scan_status(
                  ip=ip,
                  port=port,
                  status=port_status,
                  datetime_now=datetime_now)
