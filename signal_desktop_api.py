# Imports

import os

# Set env variable to local display, if this script is being executed remotely
os.environ["DISPLAY"] = ":0"

import pyautogui
import subprocess
import time
from datetime import datetime
import json
import asyncio
import pytesseract
import numpy as np
from PIL import Image
import cv2

class Signal():
    def __init__(self):
        # See if Signal Desktop app is already launched
        pids = subprocess.Popen(["pgrep", "signal-desktop"], stdout=subprocess.PIPE).communicate()[0]
        if pids != b'':
            self.get_window_id()
        else:
            # Launch signal-desktop (setting display properly with "export DISPLAY=:0" if doing this over ssh)
            os.system("signal-desktop &")

            # Find active window
            time.sleep(5) # wait for signal desktop to launch
            self.get_window_id()

            # Activate window
            self.activate_window()

            # Select conversation
            self.activate_default_conversation()

            # Minimize window
            self.minimize_window()

    def close(self):
        os.system("pkill -f signal-desktop")

    def get_window_id(self):
        # Find active window
        window_ids = subprocess.Popen(["xdotool", "search", "--name", "Signal"], stdout=subprocess.PIPE).communicate()[0]
        self.window_id = window_ids.split()[-1].decode("utf-8")

    def minimize_window(self):
        # Minimize window
        os.system(f"xdotool windowminimize {self.window_id}")

    def activate_window(self):
        # Minimize window
        os.system(f"xdotool windowactivate {self.window_id}")

    def activate_default_conversation(self):
        # Find and click on conversation icon
        self.activate_window()
        x, y = pyautogui.locateCenterOnScreen(
            os.path.join(f"{os.path.sep}".join(os.path.abspath(__file__).split(os.path.sep)[0:-1]), 'interface_pictures', 'signal_conversation_icon.png'),
            confidence=0.4
        )
        pyautogui.click(x, y)
        pyautogui.scroll(-20, x=200, y=0) #scroll to bottom of conversation window

    def send_message(self, message):
        self.activate_default_conversation()

        # Find and click on the message bar
        x, y = pyautogui.locateCenterOnScreen(
            os.path.join(f"{os.path.sep}".join(os.path.abspath(__file__).split(os.path.sep)[0:-1]), 'interface_pictures', 'signal_message_bar.png'),
            confidence=0.4
        )
        pyautogui.click(x, y)

        # Type a message (single-line only)
        pyautogui.typewrite(message.strip() + '\n', interval=0.05)

    async def check_for_new_messages(self):
        while True:
            print("Checking for new messages...")
            current_time = time.time()
            with open(os.path.expanduser("~/.config/Signal/logs/app.log"), 'r') as f: #monitor logs for indicates of new messages
                lines = f.readlines()
                for line in lines[-5:]:
                    if "PUT " in line and "[REDACTED]" in line: # check for message indicating that a message was recieved
                        d = json.loads(line)
                        utc_time = datetime.strptime(d["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
                        epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
                        if current_time - epoch_time < 1: # message less than 2 seconds ago
                            # Activate the Signal desktop window
                            self.activate_window()
                            await asyncio.sleep(1)
                            self.activate_default_conversation()

                            # Find message bar to localize OCR region
                            x, y = pyautogui.locateCenterOnScreen(
                                os.path.join(f"{os.path.sep}".join(os.path.abspath(__file__).split(os.path.sep)[0:-1]), 'interface_pictures', 'signal_message_bar.png'),
                                confidence=0.4
                            )
                            # Use pytesseract to extract the messages
                            im = pyautogui.screenshot()
                            cropped_im = im.crop((x-250, y-500, x+250, y-15))

                            kernel = np.ones((3,3),np.uint8)
                            erode = cv2.dilate(np.array(cropped_im), kernel, iterations=3)

                            lower = np.array([230,230,230])
                            upper = np.array([240,240,240])

                            mask = cv2.inRange(erode, lower, upper)
                            res = cv2.bitwise_and(np.array(cropped_im), np.array(cropped_im), mask=mask)
                            res[res==0] = 255

                            message_text = pytesseract.image_to_string(res, config="--psm 3")

                            # hueristic to get the most recent message only
                            if len(message_text.split('\n\n')) >= 2:
                                message_text = message_text.split('\n\n')[-1].strip()
                            else:
                                message_text = message_text.strip()

                            # Get the latest message
                            print(f"Message Text: {message_text}")

                            # Minimize
                            self.minimize_window()
                            break

                await asyncio.sleep(1)


if __name__ == "__main__":
    S = Signal()
    S.send_message("API: I am now online!")
    asyncio.run(S.check_for_new_messages())