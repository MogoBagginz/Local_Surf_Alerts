#!/usr/bin/env python3
"""
notification size : length = 56 characters (characters overflow to next line
giving you more lines
                    hight = title + 14 lines




   12345678901234567890123456789012345678901234567890123456
1 |_______| Day1 | Day2 | Day3 | Day4 | Day5 | Day6 | Day7 
2 |       |SwMeWi|061218|SwMeWi|SwMeWi|SwMeWi|SwMeWi|SwMeWi|  
3 |spot  6|1280ON| 
4 |1    12|1150SO|      |
5 |     18|1030OF|
6 |spot  6|**    |      |
7 |2    12|****  |
8 |     18|**    |      |
9 |spot  6|**    |
10|3    12|*     |      |
11|     18|      |
12|spot Sw|      |121110|  
13|4    Me|      |805030|
14|     Wi|      |SOSOOF|
"""
import subprocess

def send_notification(title, message):
    formatted_message = f"<font color='red'>{message}</font>"
    command = ['termux-notification', '--title', title, '--content',
               formatted_message]
    subprocess.run(command, check=True)
