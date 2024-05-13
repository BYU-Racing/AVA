from enum import Enum


MPS = 0.000278
PARTITION = 1000.
S2MIN = 60
UNIT_PERCENT = 100
BRAKE_MAX = 1024 / UNIT_PERCENT
THROT_MAX = 2185 / UNIT_PERCENT
THEME = ["Arduino", "Jarvis", "Daylight"]
SELECTED_THEME = THEME[1]
SHOW_INSTANTS = False

REAL_DATA = True
DATA_PATH = 'Data/'
DEFAULT_FILE = "Master"
FILE_TYPE = ".csv"
DEFAULT_SOURCE = DATA_PATH + DEFAULT_FILE + FILE_TYPE
LOCAL_HOST = "http://127.0.0.1:8050/"
CHROME = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"

# convert each sensor to a number
class Sensor(Enum):
    THROT = 192
    BRAKE = 11
    SWITCH = 15
    DAMP2 = 12

    DAMP1 = 13
    DAMP3 = 14
    DAMP4 = 10
    ANGLE = 4
    TIRE1 = 5
    TIRE2 = 6
    TIRE3 = 7
    TIRE4 = 8
    TEMP = 16
    LIGHT = 17
    GFORCE = 18
    SPEED = 19
    GPS = 20


# dictionary that maps indices to sensor values for the button toggle callback function
button_sensor_map = {
    0: Sensor.THROT.value,
    1: Sensor.BRAKE.value,
    2: [Sensor.TIRE1.value, Sensor.TIRE2.value, Sensor.TIRE3.value, Sensor.TIRE4.value],
    3: Sensor.ANGLE.value,
    4: [Sensor.DAMP1.value, Sensor.DAMP2.value, Sensor.DAMP3.value, Sensor.DAMP4.value],
    5: Sensor.TEMP.value,
    6: Sensor.GFORCE.value
}

# convert each sensor index to its abbreviated name
sensor_names = {
    Sensor.THROT: "THROTTLE",
    Sensor.BRAKE: "BRAKE",
    Sensor.SWITCH: "SWITCH",
    Sensor.ANGLE: "ANGLE",
    Sensor.TIRE1: "TIRE1",
    Sensor.TIRE2: "TIRE2",
    Sensor.TIRE3: "TIRE3",
    Sensor.TIRE4: "TIRE4",
    Sensor.DAMP1: "DAMP1",
    Sensor.DAMP2: "DAMP2",
    Sensor.DAMP3: "DAMP3",
    Sensor.DAMP4: "DAMP4",
    Sensor.TEMP: "TEMP",
    Sensor.LIGHT: "LIGHT",
    Sensor.GFORCE: "GFORCE",
    Sensor.SPEED: "SPEED",
    Sensor.GPS: "GPS",
}

# convert an index to a sensor display name
sensors = {
    Sensor.THROT: 'Throttle Position',
    Sensor.BRAKE: 'Brake Pressure',
    Sensor.SWITCH: 'Power Switch',
    Sensor.ANGLE: 'Steering Wheel Angle',
    Sensor.TIRE1: 'Front Left Tire',
    Sensor.TIRE2: 'Front Right Tire',
    Sensor.TIRE3: 'Back Left Tire',
    Sensor.TIRE4: 'Back Right Tire',
    Sensor.DAMP1: 'Front Left Damper',
    Sensor.DAMP2: 'Front Right Damper',
    Sensor.DAMP3: 'Back Left Damper',
    Sensor.DAMP4: 'Back Right Damper',
    Sensor.TEMP: 'Battery Temperature',
    Sensor.LIGHT: 'Rain Light',
    Sensor.GFORCE: 'G-Force',
    Sensor.SPEED: 'Vehicle Speed',
    Sensor.GPS: 'GPS Position',
}


# sensor constants
weights = {
    "W_THROT": 0.0,
    "W_BRAKE": 0.0,
    "W_SWITCH": 0.0,
    "W_ANGLE": 0.0,
    "W_TIRE1": 0.0,
    "W_TIRE2": 0.0,
    "W_TIRE3": 0.0,
    "W_TIRE4": 0.0,
    "W_DAMP1": 0.0,
    "W_DAMP2": 0.0,
    "W_DAMP3": 0.0,
    "W_DAMP4": 0.0,
    "W_TEMP": 0.0,
    "W_LIGHT": 0.0,
    "W_GFORCE": 0.0,
}

biases = {
    "B_THROT": 0.0,
    "B_BRAKE": 0.0,
    "B_SWITCH": 0.0,
    "B_ANGLE": 0.0,
    "B_TIRE1": 0.0,
    "B_TIRE2": 0.0,
    "B_TIRE3": 0.0,
    "B_TIRE4": 0.0,
    "B_DAMP1": 0.0,
    "B_DAMP2": 0.0,
    "B_DAMP3": 0.0,
    "B_DAMP4": 0.0,
    "B_TEMP": 0.0,
    "B_LIGHT": 0.0,
    "B_GFORCE": 0.0,
}

minimums = {
    "N_THROT": 0.0,
    "N_BRAKE": 0.0,
    "N_SWITCH": 0.0,
    "N_ANGLE": 0.0,
    "N_TIRE1": 0.0,
    "N_TIRE2": 0.0,
    "N_TIRE3": 0.0,
    "N_TIRE4": 0.0,
    "N_DAMP1": 0.0,
    "N_DAMP2": 0.0,
    "N_DAMP3": 0.0,
    "N_DAMP4": 0.0,
    "N_TEMP": 0.0,
    "N_LIGHT": 0.0,
    "N_GFORCE": 0.0,
}

maximums = {
    "X_THROT": 1.0,
    "X_BRAKE": 1.0,
    "X_SWITCH": 1.0,
    "X_ANGLE": 1.0,
    "X_TIRE1": 1.0,
    "X_TIRE2": 1.0,
    "X_TIRE3": 1.0,
    "X_TIRE4": 1.0,
    "X_DAMP1": 1.0,
    "X_DAMP2": 1.0,
    "X_DAMP3": 1.0,
    "X_DAMP4": 1.0,
    "X_TEMP": 1.0,
    "X_LIGHT": 1.0,
    "X_GFORCE": 1.0,
}

# theme customization
themes = {"Arduino": {  # theme name
    "color": {  # color palette for graphs and backgrounds
        0: ["gray", "rgba(60,60,60,1)", "#3C3C3C"],  # assigned to overall background
        1: ["dark-gray", "rgba(40,40,40,1)", "#222222"],  # subplot background to differentiate from background
        2: ["green", "rgba(0,187,0,1)", "#00BB00"],  # Text color
        3: ["white", "rgba(255,2555,255,1)", "#FFFFFF"],  # Alternate text color, also just white
        4: ["black", "rgba(0,0,0,1)", "#000000"],  # Steering wheel color, also just black
    },
    "trace": {
        0: ["green", "rgba(0,187,0,1)", "#00BB00"],  # color for traces and bar charts
        1: ["red", "rgba(187,0,0,1)", "#BB0000"],
        2: ["green", "rgba(0,187,0,1)", "#00BB00"],  # color for traces and bar charts
        3: ["green", "rgba(0,187,0,1)", "#00BB00"],
        4: ["green", "rgba(0,187,0,1)", "#00BB00"],  # color for traces and bar charts
        5: ["green", "rgba(0,187,0,1)", "#00BB00"],
        6: ["green", "rgba(0,187,0,1)", "#00BB00"],  # color for traces and bar charts
    },
    "size": {
        "large": "22",  # large text like graph titles
        "medium": "16",  # medium text like like legends
        "small": "14",  # small text like graph ticks
        "mini": "10",  # mini text like graph ticks
    },
    "font": {
        "title": "Courier New",  # dashboard title
        "p": "Courier New",  # most text
        "graph": "Courier New",  # alt text font for some graphs
    }
},
    "Jarvis": {
        "color": {
            0: ["black", "rgba(24,24,24,1)", "#181818"],  # assigned to overall background
            1: ["dark-gray", "rgba(42, 45, 46, 1)", "#2A2D2E"],  # subplot background to differentiate from background
            2: ["neon_blue", "rgba(84, 192, 254, 1)", "#54C0FE"],  # Text color
            3: ["white", "rgba(238, 238, 238, 1)", "#EEEEEE"],  # Alternate text color, also just white
            4: ["dark-gray", "rgba(216, 216, 216, 1)", "#888888"],  # Steering wheel color, also just black
        },
        "trace": {
            0: ["neon_blue", "rgba(2, 255, 252, 1)", "#02fffc"],
            1: ["neon_yellow", "rgba(248, 255, 51, 1)", "#f8ff33"],
            2: ["neon_blue", "rgba(2, 255, 252, 1)", "#02fffc"],
            3: ["olive", "rgba(2, 207, 252, 1)", "#02cffc"],
            4: ["pond", "rgba(2, 255, 220, 1)", "#02ffcc"],
            5: ["forest_idk_main", "rgba(2, 169, 252, 1)", "#029ffc"],
            6: ["white", "rgba(255,255,255,1)", "#FFFFFF"],  # Alternate text color, also just white
        },
        "size": {
            "large": "24",
            "medium": "18",
            "small": "15",
            "mini": "10",
        },
        "font": {
            "title": "Arial, sans-serif",
            "p": "Arial, sans-serif",
            "graph": "Arial, sans-serif",
        }
    },
    "Daylight": {
        "color": {
            0: ["white", "rgba(255,255,255,1)", "#FFFFFF"],  # assigned to overall background
            1: ["light-gray", "rgba(239, 239, 239,1)", "#EEEEEE"],
            # subplot background to differentiate from background
            2: ["black", "rgba(0,0,0,1)", "#000000"],  # Text color
            3: ["black", "rgba(0,0,0,1)", "#000000"],  # Alternate text color, also just white
            4: ["black", "rgba(0,0,0,1)", "#000000"],  # Steering wheel color, also just black
        },
        "trace": {
            0: ["red", "rgba(255,0,0,1)", "#ff0000"],
            1: ["red", "rgba(255,0,0,1)", "#ff0000"],
            2: ["red", "rgba(255,0,0,1)", "#ff0000"],
            3: ["red", "rgba(255,0,0,1)", "#ff0000"],
            4: ["red", "rgba(255,0,0,1)", "#ff0000"],
            5: ["red", "rgba(255,0,0,1)", "#ff0000"],
            6: ["red", "rgba(255,0,0,1)", "#ff0000"],
        },
        "size": {
            "large": "28",
            "medium": "22",
            "small": "18",
            "mini": "12",
        },
        "font": {
            "title": "Arial, sans-serif",
            "p": "Arial, sans-serif",
            "graph": "Arial, sans-serif",
        }
    }
}
