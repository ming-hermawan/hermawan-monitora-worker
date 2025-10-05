import json
import redis
import const
from datetime import datetime
from string import Template

from conf import conf


class hmon_redis:

    __SERVER_PORT_SCAN_KEY = Template("pubsub:$ip:$port")
    __LAST_SERVER_PORT_SCAN_KEY = Template("last:$ip:$port")

    def __redis_decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    result = func(*args, **kwargs)
                except redis.exceptions.ConnectionError:
                    continue
                break
            return result
        return wrapper

    @__redis_decorator
    def __set(self, key, val):
        self.__redis_obj.set(key, val)

    @__redis_decorator
    def __get(self, key):
        return self.__redis_obj.get(key)

    @__redis_decorator
    def __publish(self, key, val):
        self.__redis_obj.publish(key, val)

    def __init__(self):
        conf_obj = conf.get_instance()
        self.__redis_obj = redis.StrictRedis(
          host=conf_obj.get_redis_host(),
          port=conf_obj.get_redis_port(),
          password=conf_obj.get_redis_pwd(),
          decode_responses=True,
          db=conf_obj.get_redis_db(),
          socket_connect_timeout=conf_obj.get_redis_socket_connect_timeout(),
          socket_timeout=conf_obj.get_redis_socket_timeout(),
          ssl=conf_obj.get_redis_ssl(),
          ssl_cert_reqs=conf_obj.get_redis_ssl_cert_reqs(),
          ssl_certfile=conf_obj.get_redis_client_crt_filepath(),
          ssl_keyfile=conf_obj.get_redis_client_key_filepath(),
          ssl_ca_certs=conf_obj.get_redis_client_ca_filepath(),
        )

    def set_ports_scan_status(self, status: str):
        self.__set('ports-scan-status', status)

    def get_ports_scan_status(self):
        return self.__get('ports-scan-status')

    def publish_port_scan_result(self,
                                 ip: str,
                                 port: int,
                                 status: str):
        key = self.__SERVER_PORT_SCAN_KEY.substitute(
          ip=ip,
          port=port)
        ts = int(datetime.now().timestamp() * 1000000)
        val = {
          "status": status,
          "time": ts}
        self.__publish(key, json.dumps(val))

    def set_last_ports_scan_status(self,
                                   ip: str,
                                   port: int,
                                   status: str,
                                   datetime_now: datetime):
        key = self.__LAST_SERVER_PORT_SCAN_KEY.substitute(
          ip=ip,
          port=port)
        ts = int(datetime.now().timestamp() * 1000000)
        val = {
          "status": status,
          "from_time": ts}
        self.__set(key, status)

    def get_last_ports_scan_status(self,
                                   ip: str,
                                   port: int):
        key = self.__LAST_SERVER_PORT_SCAN_KEY.substitute(
          ip=ip,
          port=port)
        return json.loads(self.__get(key))
