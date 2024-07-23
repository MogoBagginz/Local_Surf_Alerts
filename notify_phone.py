#!/usr/bin/env python3

import os

def send_notification(title, message):
    os.system(f"termux-notification --title '{title}' --context '{message}'")
