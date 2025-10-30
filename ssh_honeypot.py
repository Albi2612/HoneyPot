# loging is used to log our code
import logging
# This creates a file to write the logging event
from logging.handlers import RotatingFileHandler
# A framework for SSH connection
import paramiko
# Connecting to the network
import socket
# Threads allows multiple task at the same time
import threading

logging_format = logging.Formatter('%(message)s')  # Formats the message into strings
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"

# host_key = 'server.key'
host_key = paramiko.RSAKey(filename='server.key')

funnel_logger = logging.getLogger('funnel_logger')  # We are initialising the logger
funnel_logger.setLevel(logging.INFO)
"""
Sets minium security level
Out of 5 standards logging event it only ignores debug
This avoids making the logger too noisy
"""

funnel_handler = RotatingFileHandler('audits.log', maxBytes=2000, backupCount=5)
# backupCount allows 5 old logs in system
funnel_handler.setFormatter(logging_format)  # Implements line no.6
funnel_logger.addHandler(funnel_handler)  # adding all the features of funnel handler to funnel logger

# This log is created to track cmd lines and credential audit
cred_logger = logging.getLogger('cred_logger')
cred_logger.setLevel(logging.INFO)
cred_handler = RotatingFileHandler('cmd_audits.log', maxBytes=2000, backupCount=5)
cred_handler.setFormatter(logging_format)
cred_logger.addHandler(cred_handler)

def emulated_shell(channel, client_ip):
    channel.send(b'corporate-jumpbox2$')
    command = b""
    while True:
        char = channel.recv(1)
        if not char:
            channel.close()
            break
        channel.send(char)
        command += char
        if char == b'\r':
            if command.strip() == b'exit':
                response = b'\n goodbye! \n'
                cred_logger.info(f'Command {command.strip().decode()} executed by {client_ip}')
                channel.send(response)
                channel.close()
                break
            elif command.strip() == b'pwd':
                response = b'\\user\\local\\' + b'\r\n'
                cred_logger.info(f'Command {command.strip().decode()} executed by {client_ip}')
            elif command.strip() == b'whoami':
                response = b"\n" + b"corpuser1" + b"\r\n"
                cred_logger.info(f'Command {command.strip().decode()} executed by {client_ip}')
            elif command.strip() == b'ls':
                response = b"\n" + b"jumpbox1.conf" + b'\r\n'
                cred_logger.info(f'Command {command.strip().decode()} executed by {client_ip}')
            elif command.strip() == b'cat jumpbox1.conf':
                response = b"\n" + b"Go to deeboodah.com" + b'\r\n'
                cred_logger.info(f'Command {command.strip().decode()} executed by {client_ip}')
            else:
                response = b"\n" + bytes(command.strip()) + b"\r\n"
                cred_logger.info(f'Command {command.strip().decode()} executed by {client_ip}')

            channel.send(response)
            channel.send(b'corporate-jumpbox2$ ')
            command = b""

# SSH Server + Sockets

class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client {self.client_ip} attempted connection with' + f'username: {username}'
                           + f"password: {password}")
        cred_logger.info(f"{self.client_ip}, {username}, {password}")
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True


def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"{client_ip} is connected to the server.")

    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        server = Server(client_ip=client_ip, input_username=username, input_password=password)

        transport.add_server_key(host_key)

        transport.start_server(server=server)

        channel = transport.accept(100)

        if channel is None:
            print("No channel was opened to the screen.")

        standard_banner = "Welcome to Ubuntu 24.04 LTS (Noble Numbat)!\r\n\r\n"
        channel.send(standard_banner)
        emulated_shell(channel, client_ip=client_ip)

    except Exception as error:
        print(error)
        print("!!! ERROR !!!")

    finally:
        try:
            transport.close()
        except Exception as error:
            print(error)
            print("ERROR")
        client.close()


# Provision SSH-based Honeypot

def honeypot(address, port, username, password):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))

    socks.listen(100)
    print(f"SSH server is listening on {port}.")

    while True:
        try:
            client, addr = socks.accept()
            # Creating a new thread that runs client_handle in the background
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.start()

        except Exception as error:
            print(error)


honeypot('127.0.0.1', 2223, username=None, password=None)

