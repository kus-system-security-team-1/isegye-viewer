import psutil
import socket


class ProcessService:
    def __init__(self, config):
        self.config = config

    def _get_protocol_name(self, type):
        if type == socket.SOCK_STREAM:
            return "TCP"
        elif type == socket.SOCK_DGRAM:
            return "UDP"
        elif type == socket.SOCK_RAW:
            return "RAW"
        return "UNKNOWN"

    def show_network_packets(self):
        connections = psutil.net_connections()
        info = []
        for conn in connections:
            pid = conn.pid
            if pid is not None:
                process = psutil.Process(pid)
                protocol = self._get_protocol_name(conn.type)
                laddr = (
                    f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
                )
                raddr = (
                    f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
                )
                status = conn.status
                info.append(
                    {
                        "pid": pid,
                        "process": process.name(),
                        "protocol": protocol,
                        "local_address": laddr,
                        "remote_address": raddr,
                        "status": status,
                    }
                )
        return info
