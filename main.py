#!/usr/bin/python3

import requests
import logging
import json
import subprocess
import datetime
import pandas
from requests.auth import HTTPDigestAuth


def get_data(date, hub, pwd, url, index):
    today_list = str(date).split("-")
    today_new = today_list[0] + "-" \
        + str(int(today_list[1])) + "-" \
        + str(int(today_list[2]))

    return subprocess.check_output(
        ['curl',
         "--digest",
         "-u",
         str(hub) + ":" + str(pwd),
         "-H",
         'accept: application/json',
         "-H",
         'content-type: application/json',
         "--compressed",
         "https://" + str(url) + "/cgi-jday-" + str(index) + "-" + today_new])


def get_status(hub, pwd, url):

    return subprocess.check_output(
        ['curl',
         "--digest",
         "-u",
         str(hub) + ":" + str(pwd),
         "-H",
         'accept: application/json',
         "-H",
         'content-type: application/json',
         "--compressed",
         "https://" + str(url) + "/cgi-jstatus-*"])


def create_new_zappi_data(date, hub_serial, hub_pwd):
    director_url = "https://director.myenergi.net"
    
    # request connection to the wallbox
    response = requests.get(director_url, auth=HTTPDigestAuth(hub_serial, hub_pwd))
    
    # check whether the connection worked (200) or not
    if str(response) != "<Response [200]>":
        logging.info("Verbindung zur Wallbox konnte NICHT hergestellt werden!")
        raise ConnectionError
    
    # get the server url of the wallbox
    server_URL = response.headers['X_MYENERGI-asn']
    
    output_zappi = json.loads(get_data(date=date,
                                       hub=hub_serial,
                                       pwd=hub_pwd,
                                       url=server_URL,
                                       index="Z" + str(hub_serial)))
    
    # 11705611 sno H
    
    df = pandas.DataFrame.from_records(list(output_zappi.values())[0])
    df = df.fillna(0)
    for i in ["yr", "mon", "dom", "hr", "min"]:
        df[i] = df[i].astype(int)
        #df[i] = df[i].astype(str)
    for num, row in df.iterrows():
        df.loc[num, "Datum"] = datetime.datetime(year=row["yr"],
                                             month=row["mon"],
                                             day=row["dom"],
                                             hour=row["hr"],
                                             minute=row["min"])
        
    df = df.drop(columns=["yr", "mon", "dom", "dow", "hr", "min"])
    df = df.set_index("Datum")
    
    # change frequency data format to decimal
    df.frq = df.frq / 100
    # change voltage data format to decimal
    df.v1 = df.v1 / 10
    # change imported Energy to kWh
    df.imp = df.imp / 3600000
    df.exp = df.exp / 3600000
    df.pect1 = df.pect1 / 3600000
    df.pect2 = df.pect2 / 3600000
    df.pect3 = df.pect3 / 3600000
    df.nect1 = df.nect1 / 3600000
    df.nect3 = df.nect3 / 3600000
    
    
    df["Export in kWh"] = df.pect3 + df.nect1
    df["Import in kWh"] = df.pect1 + df.pect2 + df.nect3
    
    df["Diff_Import"] = df.imp - df["Import in kWh"]
    df["Diff_Export"] = df.exp - df["Export in kWh"]
    
    df = df.rename(columns={"frq": "Netzfrequenz in Hz",
                            "v1": "Spannung Phase 1 in V",
                            "imp": "Energieimport in kWh",
                            "pect1": "bezogene Energie Phase 1 in kWh",
                            "pect2": "bezogene Energie Phase 2 in kWh",
                            "nect3": "bezogene Energie Phase 3 in kWh", # TODO hier muss die richtung im Verteilerschrank anders rum
                            "pect3": "abgegebene Energie Phase 3 in kWh", # TODO hier muss die richtung im Verteilerschrank anders rum
                            "nect1": "abgegebene Energie Phase 1 in kWh" })
    df.to_csv("Zappi_output.csv")
    
