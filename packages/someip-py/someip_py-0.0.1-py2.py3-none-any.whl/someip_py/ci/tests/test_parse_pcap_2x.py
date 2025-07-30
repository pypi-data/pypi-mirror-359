import os

from someip_py import SOMEIPService


def test_parse_someip_pcap(pcap_file, output=None):
    someip_service = SOMEIPService()
    someip_service.parse_pcap(pcap_file, output=output)


if __name__ == "__main__":
    test_parse_someip_pcap(os.path.join(os.path.dirname(__file__), "1.pcap"))
