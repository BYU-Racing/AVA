import pandas as pd
import numpy as np
import os
import warnings

import Config
from Config import *


"""
Assumptions: OUTDATED
1. Data is sent in IEEE 64 bit floating point binary representation
2. Time is sent as number of milliseconds since the start
3. We have control over how we encode data and timestamps
4. We have control over how we encode the entire signal (metadata)
5. CSV File has one signal per line and optionally one field per column
6. Signals follow CAN Bus Protocol Draft format

Corrections #TODO
1. Time is an unsigned long in milliseconds from power on
2. Data is a 2 byte ADC range from zero to max, unique for each sensor. Only the first 10 bits are meaningful
3. ID is an int from 0 to (total number of sensors)
4. Each run starts with a delimiter
5. Input file is a CSV
"""


def readData(filename, return_times=False, verbose=False):
    """
    Read data from a csv file filename into a dictionary
    Parameters:
        filename (string): name of the file to read
        return_times (bool): whether to return the start and end times
        verbose (bool): whether to print out the data
    Returns:
        all_data (dictionary): data from the csv stored, converted, and parsed in a dictionary
                               maps sensor id (int) to a pandas dataframe with columns 'Time' and 'Data'
        start_time (float): start time of the data if requested
        end_time (float): end time of the data if requested
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # read data. idk why there's whitespace but that's how the data comes
        df = pd.read_csv(filename, sep=',')
        df.columns = df.columns.str.strip()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(pd.NA).astype('Int64')

        # get the first and last timestamps
        if return_times:
            start_time = df['Time'][0] / PARTITION / S2MIN
            end_time = df['Time'][len(df['Time']) - 1] / PARTITION / S2MIN
            if verbose:
                print("Start Time:", start_time, "minutes")
                print("End Time:", end_time, "minutes")

        # split data into separate sensors
        all_data = {}
        for sensor_id in Sensor:
            key = sensor_id.value
            if key in df['ID'].unique():
                all_data[key] = df[df["ID"] == key]
                all_data[key].loc[:, 'Time'] = convertTime(all_data[key]['Time'])

                if key == Sensor.SWITCH.value or key == Sensor.LIGHT.value:
                    # this just returns the data as is
                    all_data[key].loc[:, 'Data'] = convertRawData(all_data[key]['Data0'])
                else:
                    is_throttle = key == Sensor.THROT.value
                    all_data[key].loc[:, 'Data'] = convertAnalog(all_data[key]['Data0'],
                                                                 all_data[key]['Data1'],
                                                                 is_throttle)
                # ID and other data columns are now irrelevant and can be dropped
                all_data[key] = all_data[key][['Time', 'Data']]
                if verbose:
                    print("\n\nSensor", key, "Data")
                    print(all_data[key].describe())
        if return_times:
            return all_data, start_time, end_time
        return all_data


# def readRealData(filename):
#     """
#     Read data from a csv file 'filename' into a dictionary
#     Parameters:
#         filename (string): name of the file to read
#     Returns:
#         all_data (dictionary): data from the csv stored, converted, and parsed in a dictionary
#     """
#     # read data
#     df = pd.read_csv(filename, sep=',', usecols=['ID', 'Timestamp', 'Data'])
#
#     # convert from binary to decimal
#     df['ID'] = convertOldID(df['ID'])
#     df['Timestamp'] = convertOldTime(df['Timestamp'])
#     df['Data'] = convertOldData(df['Data'])
#
#     # fill in missing data
#     df = df.fillna(method='ffill')
#     df = prepend_zeros(df)
#
#     # split data into separate sensors
#     all_data = {}
#     for i in range(len(sensors)):
#         all_data.update({i: df[df["ID"] == sensors[i]]})
#
#     # get the last timestamp
#     duration = 0
#     for id in df['ID'].unique():
#         # Get the subset of the input dataframe for this ID
#         id_df = df[df['ID'] == id]
#
#         # Find the last timestamp for this ID
#         last_timestamp = id_df['Time'].max()
#         if duration < last_timestamp:
#             duration = last_timestamp
#
#     # return all the data in the csv
#     return all_data, duration / PARTITION

# def parseBits(signals):
#     """
#     Check a binary string to make sure it matches the CANBus format, then turn it into a dataframe
#     Parameters:
#         signals (list): list of strings of binary digits
#     Returns:
#         processed (dataframe): data parsed into rows and columns
#     """
#     protocol = [['Start of frame', 1],
#                 ['ID', 11],
#                 ['Stuff bit', 1],
#                 ['IDE', 1],
#                 ['Reserved bit', 1],
#                 ['Message length', 4],
#                 ['Timestamp', 16],
#                 ['Data field', 64],
#                 ['CRC', 15],
#                 ['CRC delimiter', 1],
#                 ['ACK slot', 1],
#                 ['ACK delimiter', 1],
#                 ['EOF', 1],
#                 ['IFS', 3],
#                 ['Total', 121], ]
#
#     processed = []
#     for signal in signals:
#
#         # check data type
#         if type(signal) is not str:
#             raise TypeError(f"Signal is not of type string. Instead received {type(signal)}."
#                             f"\nSignal: {signal}")
#
#         # check signal length
#         if len(signal) != protocol[-1][1]:
#             raise ValueError(f"Signal is not the right length. Expected {protocol[-1][1]} but received {len(signal)}."
#                              f"\nSignal: {signal}")
#
#         # create a list of signals divided into fields
#         parsed = []
#         for field in protocol[:-1]:
#             parsed.append(signal[:field[1]])
#             signal = signal[field[1]:]
#         processed.append(parsed)
#
#     # return the full data frame
#     return pd.DataFrame(processed)

# def convertOldTime(timestamp):
#     """
#     Convert binary timestamp into human-readable text
#     Parameters:
#         timestamp (string or dataframe): time as a string of binary digits
#     Returns:
#         time (int or dataframe): formatted time
#     """
#     # case if parameter is a string
#     if type(timestamp) is str:
#         return int(str(timestamp), 2) / PARTITION
#
#     # case if parameter is a dataframe
#     return pd.DataFrame([int(str(time), 2) / PARTITION for time in timestamp])

def convertTime(timestamp):
    """
    Read in timestamp in milliseconds and convert to seconds
    Parameters:
        timestamp (int or dataframe): time as a string decimal digits
    Returns:
        time (float or dataframe): formatted time in seconds
    """
    return timestamp / PARTITION

# def convertOldID(id_sensor):
#     """
#     Convert a binary ID into an integer
#     Parameters:
#         id_sensor (string or dataframe of strings): sensor id in binary
#     Returns:
#         id (int or dataframe of ints): sensor id in decimal
#     """
#     # case if parameter is a string
#     if type(id_sensor) is str:
#         return sensors[int(str(id_sensor), 2)]
#
#     # case if parameter is a dataframe
#     return pd.DataFrame([sensors[int(str(i), 2)] for i in id_sensor])

# def convertID(id_sensor):
#     """
#     Read in sensor ID and convert to a string name
#     Parameters:
#         id_sensor (string or dataframe of strings): sensor id as an integer
#     Returns:
#         id (string or dataframe of strings): sensor name
#     """
#     # case if parameter is a string
#     if type(id_sensor) is str:
#         return sensors[int(id_sensor)]
#
#     # case if parameter is a dataframe
#     return pd.DataFrame([sensors[int(i)] for i in id_sensor])


# def convertOldData(data):
#     """
#     Convert binary data into a float
#     Parameters:
#         data (string or dataframe of strings): data in binary as a string
#     Returns:
#         data (int or dataframe of ints): data in decimal
#     """
#     # case if parameter is a string
#     if type(data) is str:
#         return BitArray(bin=str(data)).float
#
#     # case if parameter is a dataframe
#     return pd.DataFrame([BitArray(bin=str(d)).float for d in data])

def convertAnalog(low_byte, high_byte, throttle=False):
    """
    Read in 2 columns analog data and convert to a decimal
    Parameters:
        low_byte (int or dataframe of ints): low byte of throttle data
        high_byte (int or dataframe of ints): high byte of throttle data
        throttle (bool): whether the data is throttle or analog
    Returns:
        data (int or dataframe of ints): data in decimal
    """
    alpha = 255 if throttle else 100
    if throttle:
        return low_byte + high_byte * alpha
    return high_byte + low_byte * alpha


def convertRawData(data):
    """
    Read in 1 column sensor data and convert to a float
    Parameters:
        data (string or dataframe of strings): data in decimal as a string
    Returns:
        data (float or dataframe of floats): data in decimal
    """
    return data


def convert_position(speed, time, angle):
    """
    Convert timestamped speed and steering wheel angle to current
    track position.
    :param speed: (list) a list of speeds in miles per hour as floats
    :param time: (list) as list of timestamps in seconds as floats
    :param angle: (list) a list of wheel angles in degrees as floats
    :return: x and y positions (list, list) of floats
    """
    # convert MPH to MPS and make distance traveled per second
    distance = [s * MPS * t for s, t in zip(speed, time)]
    theta = 0
    x = 0
    y = 0

    x_val = [0] * len(distance)
    y_val = [0] * len(distance)
    angle = [np.deg2rad(a) for a in angle]

    for i in range(len(distance)):
        theta += angle[i]

        x += distance[i] * np.cos(theta)
        x_val[i] = x

        y += distance[i] * np.sin(theta)
        y_val[i] = y

    return x_val, y_val


def convert_sensor_data(sensor, data):
    """
    Convert raw sensor data to a float accounting for weights and biases
    :param sensor: (string) the name of the sensor
    :param data: (int) the raw data from the sensor
    :return: (float) the converted data
    """
    weight = "W_" + sensor
    bias = "B_" + sensor
    return (data - Config.biases[bias]) * Config.weights[weight]


# def prepend_zeros(df):
#     # Create a new empty dataframe to hold the output
#     output_df = pd.DataFrame()
#
#     # Loop over each unique ID in the input dataframe
#     for id in df['ID'].unique():
#         # Get the subset of the input dataframe for this ID
#         id_df = df[df['ID'] == id]
#
#         # Find the first timestamp for this ID
#         first_timestamp = id_df['Time'].min()
#
#         # Create a new dataframe with rows for every millisecond between
#         # zero and the first timestamp for this ID
#         new_rows = []
#         for timestamp in range(0, first_timestamp + 1):
#             new_rows.append({'ID': id, 'Time': timestamp, 'Data': 0})
#         new_df = pd.DataFrame(new_rows)
#
#         # Append the original dataframe to the new dataframe and fill any
#         # missing values with zeros
#         merged_df = pd.merge(new_df, id_df, on=['ID', 'Time'], how='outer').fillna(0)
#
#         # Add the merged dataframe to the output dataframe
#         output_df = output_df.append(merged_df)
#
#     # Sort the output dataframe by ID and timestamp
#     output_df = output_df.sort_values(['Timestamp', 'ID'])
#
#     return output_df


def get_latest_data():
    """
    Find the highest numbered file in the data folder

    Returns:
        latest_file (string): the name of the latest file
    """
    # find all files that only have numbers in their name
    files = os.listdir(Config.DATA_PATH)
    files = [f for f in files if f.split(".")[0].isdigit()]

    # sort the files by number lowest to highest and return the last file
    files.sort(key=lambda x: int(x.split(".")[0]))
    return DATA_PATH + files[-1]
