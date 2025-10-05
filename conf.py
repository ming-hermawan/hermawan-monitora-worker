import os
import logging
from dotenv import dotenv_values


class conf:

    __instance = None

    @staticmethod
    def get_instance(env_filepath: str = None):
        if conf.__instance is None:
            if env_filepath is None:
                raise Exception("No default env file!")
            else:
                conf(env_filepath)
        return conf.__instance

    def __init__(self, env_filepath: str):
        if conf.__instance is not None:
            raise Exception(
              'This class is a singleton, \
use conf.get_instance() instead!'
            )
        else:
            if env_filepath is not None:
                self.__init_conf(env_filepath)
            conf.__instance = self

    def __init_conf(self, env_filepath: str):
        # Initialization
        dotenv_dict = dotenv_values(env_filepath)

        # Log Level
        self.__log_lvl = int(dotenv_dict.get('LOG_LEVEL', '20'))

        # Run Interval in Seconds
        self.__interval = dotenv_dict['INTERVAL']

        # Write to file?
        self.__write_to_file = True if \
            dotenv_dict.get('WRITE_TO_FILE', 'NO') == 'YES' \
            else False

        # Redis
        self.__redis_host = dotenv_dict['REDIS_HOST']
        self.__redis_port = int(dotenv_dict['REDIS_PORT'])
        self.__redis_pwd = dotenv_dict.get('REDIS_PASSWORD')
        self.__redis_db = int(dotenv_dict['REDIS_DB'])
        redis_socket_connect_timeout = dotenv_dict.get(
          'REDIS_SOCKET_CONNECT_TIMEOUT',
          '').strip()
        self.__redis_socket_connect_timeout = None if \
            redis_socket_connect_timeout == '' else \
            float(redis_socket_connect_timeout)
        redis_socket_timeout = dotenv_dict.get(
          'REDIS_SOCKET_TIMEOUT',
          '').strip()
        self.__redis_socket_timeout = None if \
            redis_socket_timeout == '' else \
            float(redis_socket_timeout)
        redis_client_crt_filepath = dotenv_dict.get(
          'REDIS_CLIENT_CRT_FILEPATH',
          '').strip()
        if redis_client_crt_filepath == '':
            self.__redis_client_crt_filepath = None
        elif not os.path.isfile(redis_client_crt_filepath):
            raise Exception("{} file is not exists!".format(
              redis_client_crt_filepath
            ))
            self.__redis_client_crt_filepath = \
                redis_client_crt_filepath
        redis_client_key_filepath = dotenv_dict.get(
          'REDIS_CLIENT_KEY_FILEPATH',
          '')
        if redis_client_key_filepath == '':
            self.__redis_client_key_filepath = None
        elif not os.path.isfile(redis_client_key_filepath):
            raise Exception("{} file is not exists!".format(
              redis_client_key_filepath
            ))
            self.__redis_client_key_filepath = \
                redis_client_key_filepath
        redis_client_ca_filepath = dotenv_dict.get(
          'REDIS_CLIENT_CA_FILEPATH',
          '')
        if redis_client_ca_filepath == '':
            self.__redis_client_ca_filepath = None
        elif not os.path.isfile(redis_client_ca_filepath):
            raise Exception("{} file is not exists!".format(
              redis_client_ca_filepath
            ))
            self.__redis_client_ca_filepath = \
                redis_client_ca_filepath
        if (
          redis_client_crt_filepath and redis_client_key_filepath
        ) or redis_client_ca_filepath:
            self.__redis_ssl = True
            self.__redis_ssl_cert_reqs = 'required'
        else:
            self.__redis_ssl = False
            self.__redis_ssl_cert_reqs = 'none'

        # Path
        self.__sqlite_db_filepath = dotenv_dict.get(
            'SQLITE_DB_FILEPATH')
        self.__log_path = dotenv_dict.get('LOG_DIRPATH')

    def get_log_lvl(self):
        return self.__log_lvl

    def get_interval(self) -> int:
        return self.__interval

    def get_redis_host(self) -> str:
        return self.__redis_host

    def get_redis_port(self) -> int:
        return self.__redis_port

    def get_redis_pwd(self) -> str:
        return self.__redis_pwd

    def get_redis_db(self) -> int:
        return self.__redis_db

    def get_redis_socket_connect_timeout(self) -> float:
        return self.__redis_socket_connect_timeout

    def get_redis_socket_timeout(self) -> float:
        return self.__redis_socket_timeout

    def get_redis_ssl(self) -> bool:
        return self.__redis_ssl

    def get_redis_ssl_cert_reqs(self) -> str:
        return self.__redis_ssl_cert_reqs

    def get_redis_client_crt_filepath(self) -> str:
        return self.__redis_client_crt_filepath

    def get_redis_client_key_filepath(self) -> str:
        return self.__redis_client_key_filepath

    def get_redis_client_ca_filepath(self) -> str:
        return self.__redis_client_ca_filepath

    def get_sqlite_db_filepath(self) -> str:
        return self.__sqlite_db_filepath

    def get_log_path(self) -> str:
        return self.__log_path

    def write_to_file(self) -> bool:
        return self.__write_to_file
