import cv2
import numpy as np
from PIL import ImageGrab
import time
import pyautogui
import random
import math
import pydirectinput as pdi
import argparse
import sys

bombkey = 'space' # Bomb keybind
sightkey = 'f7'  # Key for Bomb Sight
vckey = 'f4' # Key for Virtual Cockpit
bombbay = True # Does the plane have a bomb-bay?

screensize = pyautogui.size()
sx, sy = screensize
posofclimb = int((sy / 2) - 40) # How many pixels up from the flat mouseposition to begin climbing (the number is offset from the middle of the screen)

# UI stuff
parser = argparse.ArgumentParser()
parser.add_argument("--debug", type=lambda x: x.lower() == "true", default=False)
parser.add_argument("--bombsize", type=int, default=250)
parser.add_argument("--base", type=int, default=3)
args = parser.parse_args()

debug = args.debug
bombsize = args.bombsize
base_number = args.base

def searchScreen(timg):
    target_img_orig = cv2.imread(str(timg), cv2.IMREAD_GRAYSCALE)

    # Take a screenshot of the entire screen
    screen = np.array(ImageGrab.grab())
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    threshold = 0.4
    base_locations = []
    best_match = None
    best_val = 0
    best_template = None

    # Search at multiple scales
    for scale in np.linspace(0.3, 1.3, 101):  # Lowest (30%), Highest (130%), Number of checks (101). Searches at increments of ~0.01 (~1%)
        # Resize the template
        resized = cv2.resize(target_img_orig, (0, 0), fx=scale, fy=scale)
        tH, tW = resized.shape[:2]

        # Ignore too-small templates
        if screen_gray.shape[0] < tH or screen_gray.shape[1] < tW:
            continue

        result = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > threshold and max_val > best_val:
            best_val = max_val
            best_match = max_loc
            best_template = resized

    if best_match:
        pt = best_match
        tH, tW = best_template.shape[:2]
        cv2.rectangle(screen, pt, (pt[0] + tW, pt[1] + tH), (0, 255, 0), 2)
        base_locations.append(pt)

    if debug:
        cv2.imshow('Detected Bases', screen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(f"Scale {scale:.2f} match confidence: {max_val:.3f}")

    return base_locations, best_template

if debug:
    time.sleep(3)
pdi.press(vckey)
time.sleep(0.5)
base_locations, target_img = searchScreen("Main/BaseIdentify.png")

if base_locations:
    print("Bases found!")
    base_index = random.randint(0, len(base_locations) - 1) # Choose a random base location index
    random_base = base_locations[base_index]

    # Calculate the center coordinates of the bounding box
    center_x = random_base[0] + target_img.shape[1] // 2
    center_y = random_base[1] + target_img.shape[0] // 2

    pdi.moveTo(center_x, center_y, duration=2) # Move the mouse to the center of the detected base
    time.sleep(0.5)
    pdi.moveTo(pyautogui.position().x, pyautogui.position().y - 50, duration=3) # Begin climb
    print("Mouse moved to correct position of base, begin climbing")
    pdi.press(sightkey)

    time.sleep(90) # Give turn time and wait until minimum base distance

    # Add another searchscreen for when bombsight crosses over the base
    print("Drop payload")

    if bombbay == True:
        pdi.press(bombkey)
        time.sleep(1.5)

    # Press bomb key for the selected base
    if base_number == 3:
        for i in range(0, math.ceil(550 / bombsize)):  # Top tier (8.0 - 13.7)
            pdi.press(bombkey)
            time.sleep(0.1)
        print("Bombs away")
    elif base_number == 4:
        for i in range(0, math.ceil(800 / bombsize)):
            pdi.press(bombkey)
            time.sleep(0.1)
        print("Bombs away")

    else:
        print("Invalid base number!")

else:
    print("Could not find any bases!")
    sys.exit(1)