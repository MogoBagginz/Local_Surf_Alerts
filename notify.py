#!/usr/bin/env python3

from plyer import notification

def send_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Your Application Name'
        )
        print("Notification sent successfully!")
    except Exception as e:
        print(f"Failed to send notification: {e}")
