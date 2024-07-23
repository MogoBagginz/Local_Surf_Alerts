#!/usr/bin/env python3

import subprocess

def send_notification(title, message):
    command = ['termux-notification', '--title', title, '--content', message]
    subprocess.run(command, check=True)
