import sqlite3
import os
from conf import conf


class data:

    def get_data_ip_ports(self):
        connection_obj = sqlite3.connect(
            conf.get_instance().get_sqlite_db_filepath()
        )
        cur = connection_obj.cursor()
        cur.execute(
          '''SELECT
mp_servers.server_group,
mp_ports.ip,
mp_servers.name,
mp_ports.port,
mp_ports.name FROM mp_ports
LEFT JOIN mp_servers ON mp_servers.ip = mp_ports.ip
ORDER BY mp_ports.ip, mp_ports.port ASC''')
        rows = cur.fetchall()
        connection_obj.close()
        return rows
