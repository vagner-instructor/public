# Criado por Vagner Silva - vagner.instructor@gmail.com
# Github - https://github.com/vagner-instructor
#
# Agradecimentos para NetworkEvolution em https://www.youtube.com/watch?v=Xb-8_GvsTfs 
# Agradecimentos para Datacamp em https://www.datacamp.com/community/tutorials/reading-writing-files-python
# Agradecimentos para KyWinter em https://github.com/CiscoSE/SnortBlocklistImporter



#import shutil
import time
import argparse
import requests
import json
import os

from requests.packages import urllib3
from requests.auth import HTTPBasicAuth

# If receiving SSL Certificate Errors, un-comment the line below
urllib3.disable_warnings()

# Setup an API session
API_SESSION = requests.Session()

# Set a wait interval (in seconds) - don't make this too short or you'll get greylisted
INTERVAL = 3600

# Snort Blocklist Cache

SNORT_DATA_FILE = "blocklist.json"

# Endereço para baixar a lista do Talos
SNORT_BLOCKLIST_URL = "https://snort.org/downloads/ip-block-list"

####################
#    FUNCTIONS     #
####################


def get_blocklist():
    """Check to see if we have a cached blocklist, fetch a new one if needed, then return the results"""

    # Check to see if we have cached data
    if os.path.isfile(SNORT_DATA_FILE):
        print("Cached blocklist found.")

        # Get the delta of the current time and the file modified time
        time_delta = time.time() - os.path.getmtime(SNORT_DATA_FILE)

        # If the file is less than an hour old, use it
        if time_delta < INTERVAL:
            print("Cached blocklist was less than {} seconds old.  Using it.".format(INTERVAL))

            # Open the CONFIG_FILE and load it
            with open(SNORT_DATA_FILE, 'r') as blocklist_file:
                ip_list = json.load(blocklist_file)

        else:
            print("Cached blocklist was too old, getting a new one.")

            # Get a new blocklist
            ip_list = get_new_blocklist()

    else:
        print("No cached blocklist was found, getting a new one.")

        # Get a new blocklist
        ip_list = get_new_blocklist()

    return ip_list


def get_new_blocklist():
    """Retrieve the Snort Blocklist and return a list of IPs"""

    try:
        # Get the IP Blocklist data from Snort.org
        response = requests.get(SNORT_BLOCKLIST_URL, stream=True)

        # If the request was successful
        if response.status_code >= 200 or response.status_code < 300:

            # A placeholder list for IPs
            ip_list = []

            # Add each IP address to our ip_list
            for line in response.iter_lines():

                # Decode the line
                line = line.decode("utf-8")

                # Make sure we haven't exceeded our requests per minute maximum
                if "exceeded" in line:
                    print("It looks like we've exceeded the request maximum for the blocklist. Terminating.")
                    exit()

                if "DOCTYPE" in line:
                    print("Got garbage back from the Snort.org blocklist. Terminating.")
                    exit()

                if line:
                    ip_list.append(line)

            # Cache the data from Snort.org
            with open(SNORT_DATA_FILE, 'w') as output_file:
                json.dump(ip_list, output_file, indent=4)

            return ip_list

        else:
            print("Failed to get data from Snort.org. Terminating.")
            exit()

    except Exception as err:
        print("Unable to get the Snort.org Blocklist - Error: {}".format(err))
        exit()

#Vagner Newbie
with open ('blocklist.json') as json_file:
    block_list = json.load(json_file)
    
    
def main():
    """This is a function to run the main logic of the SnortBlocklistImporter"""

    # Get the IPs in the Snort Blocklist
    ip_list = get_blocklist()

    # Read Talos Blocklist

    #talos_list = open_snortfile()

    # Read Talos Blocklist again
    print = (block_list)
    
    
if __name__ == "__main__":

    # Set up an argument parser
    parser = argparse.ArgumentParser(description="A script to import the Snort Blocklist into ASA")
    parser.add_argument("-d", "--daemon", help="Run the script as a daemon", action="store_true")
    args = parser.parse_args()

    # Load configuration data from file

    if args.daemon:
        while True:
            main()
            print("Waiting {} seconds...".format(INTERVAL))
            time.sleep(INTERVAL)
    else:
        main()