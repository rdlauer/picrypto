import time
import json  # optional - for debugging json payloads
import notecard
from periphery import I2C
from dateutil.parser import parse
from datetime import datetime
import keys

# init the Notecard (more info at dev.blues.io)
productUID = keys.PRODUCT_UID
port = I2C("/dev/i2c-1")
card = notecard.OpenI2C(port, 0, 0)
req = {"req": "hub.set"}
req["product"] = productUID
req["mode"] = "periodic"
req["outbound"] = 600
# print(json.dumps(req)) # print/debug json
rsp = card.Transaction(req)
# print(rsp) # print debug request


def main(start_timestamp):
    """ loops through log file to get crypto hash rate """
    with open("log.txt") as fp:
        lines = fp.readlines()
        for line in lines:
            # check if this line starts with a valid date and contains "miner"
            line_timestamp = line[1:19]
            if is_date(line_timestamp) and "miner" in line:
                dt = datetime.strptime(line_timestamp, '%Y-%m-%d %H:%M:%S')
                if dt >= start_timestamp:
                    send_note(line, dt)

    time.sleep(300)  # check again in 5 minutes
    main(datetime.now())


def send_note(line, dt):
    """ extract 10s H/s value from log and send to notehub.io """
    # example from log.txt:
    # [2021-04-20 14:55:02.085]  miner    speed 10s/60s/15m 77.37 76.91 n/a H/s max 77.87 H/s
    hash_rate = line[54:line.find(" ", 54) - 1]
    ms_time = dt.timestamp() * 1000

    req = {"req": "note.add"}
    req["file"] = "crypto.qo"
    req["body"] = {"rate": hash_rate}
    req["body"] = {"time": ms_time}
    rsp = card.Transaction(req)
    # print(rsp) # debug/print request


def is_date(string, fuzzy=False):
    """ return whether the string can be interpreted as a date """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


main(datetime.now())
