#!/usr/bin/env python3
import sys
import getopt
import argparse
import re

def raw_lines(file):
    try:
        with open(file, "rb") as raw_file:
            raw_lines = raw_file.readlines()
    except Exception as e:
        print("Failed to open", file, ". Do you have the file name correct?")
        print("Error:", e)
        sys.exit(1)
    return raw_lines

def parse_file(file):
    cleanup = []
    for line in file:
        clean = line.decode('utf-8').rstrip()  # Decode bytes to string and strip trailing newline
        cleanup.append(clean)
    try:
        header = cleanup.index('BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key')
        stationStart = cleanup.index('Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs')
        del cleanup[header]
    except Exception as e:
        print("You seem to have provided an improper input file", file_name, "Please make sure you are loading an airodump csv file and not a Pcap")
        print("Error:", e)
        sys.exit(1)
    Clients = cleanup[stationStart:]  # Split off the clients into their own list
    stationStart = stationStart - 1  # Ugly hack to make sure the heading gets deleted from end of the APs List
    del cleanup[stationStart:]  # Remove all of the client info leaving only the info on available target AP's in ardump maybe I should create a new list for APs?
    lines = [cleanup, Clients]
    return lines

def join_write(data, name):
    with open(name, 'a') as file:
        for line in data[0]:
            line = line.rstrip()
            if len(line) > 1:
                file.write(line + '\n')
        for line in data[1]:
            if len(line) > 1:
                file.write(line + '\n')

def showBanner():
    print("Airodump Joiner\nJoin Two Airodump CSV Files\n\n\t-i\tInput Files [ foo_name_1 foo_name_2 foo_name_3 .....] \n\t-o\tOutput File\n")

def file_pool(files):
    AP = []
    Clients = []
    for file in files:
        ret = raw_lines(file)
        ret = parse_file(ret)
        AP.extend(ret[1])
        Clients.extend(ret[0])
    lines = [AP, Clients]
    output = sort_file(lines)
    return output

def sort_file(input):
    AP = ['BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key']
    Clients = ['\nStation MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs']
    Clients.extend(input[0])
    AP.extend(input[1])
    output = [AP, Clients]
    return output

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Airodump Joiner\nJoin Two Airodump CSV Files\n\n\t-i\tInput Files [ foo_name_1 foo_name_2 foo_name_3 .....] \n\t-o\tOutput File\n")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Airodump Joiner")
    parser.add_argument("-o", "--output", dest="output", nargs=1, required=True, help="output file to write to")
    parser.add_argument("-i", "--file", dest="filename", nargs='+', required=True, help="Input files to read data from, requires at least two arguments")

    args = parser.parse_args()
    filenames = args.filename
    outfile = args.output

    if len(filenames) < 2:
        print("You must provide at least two file names to join. IE... -i foo1.csv foo2.csv\n")
        print("Airodump Joiner\nJoin Two Airodump CSV Files\n\n\t-i\tInput Files [ foo_name_1 foo_name_2 foo_name_3 .....] \n\t-o\tOutput File\n")
        sys.exit(1)

    return_var = file_pool(filenames)
    return_var = join_write(return_var, outfile[0])
