import socket
from unittest.mock import patch, MagicMock
from modules.process.process_service import ProcessService

config = {}


def test_get_protocol_name():
    service = ProcessService(config)

    assert service._get_protocol_name(socket.SOCK_STREAM) == "TCP"
    assert service._get_protocol_name(socket.SOCK_DGRAM) == "UDP"
    assert service._get_protocol_name(socket.SOCK_RAW) == "RAW"
    assert service._get_protocol_name(1234) == "UNKNOWN"


def test_show_network_packets():
    mock_connections = [
        MagicMock(
            pid=1234,
            type=socket.SOCK_STREAM,
            laddr=MagicMock(ip="127.0.0.1", port=8080),
            raddr=MagicMock(ip="192.168.1.1", port=80),
            status="ESTABLISHED"
        ),
        MagicMock(
            pid=5678,
            type=socket.SOCK_DGRAM,
            laddr=MagicMock(ip="127.0.0.1", port=53),
            raddr=None,
            status="LISTEN"
        ),
    ]

    with patch("psutil.net_connections", return_value=mock_connections), \
         patch("psutil.Process") as MockProcess:

        MockProcess.return_value.name.return_value = "mock_process"

        service = ProcessService(config)
        result = service.show_network_packets()

        expected_result = [
            {
                "pid": 1234,
                "process": "mock_process",
                "protocol": "TCP",
                "local_address": "127.0.0.1:8080",
                "remote_address": "192.168.1.1:80",
                "status": "ESTABLISHED",
            },
            {
                "pid": 5678,
                "process": "mock_process",
                "protocol": "UDP",
                "local_address": "127.0.0.1:53",
                "remote_address": "",
                "status": "LISTEN",
            },
        ]

        assert result == expected_result
