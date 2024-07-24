#!/usr/bin/env python3
"""
notification size : length = 56 characters (characters overflow to next line
giving you more lines
                    hight = title + 14 lines
"""
import subprocess

def send_notification(title, message):
    command = ['termux-notification', '--title', title, '--content', message]
    subprocess.run(command, check=True)
