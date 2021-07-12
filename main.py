import obd
import argparse
import time
from datetime import datetime

class ObdLogger:
    def __init__(self, filename, refresh_rate_ms):
        self._filename = filename
        self._refresh_rate_ms = refresh_rate_ms

        self._commands = dict()
        self._commands['TIME'] = None
        self._commands['SPEED'] = obd.commands.SPEED
        self._commands['RPM'] = obd.commands.RPM
        self._commands['FUEL_STATUS'] = obd.commands.FUEL_STATUS
        self._commands['O2_SENSORS'] = obd.commands.O2_SENSORS
        self._commands['INTAKE_PRESSURE'] = obd.commands.INTAKE_PRESSURE
        self._commands['FUEL_INJECT_TIMING'] = obd.commands.FUEL_INJECT_TIMING
        self._commands['LONG_FUEL_TRIM_1'] = obd.commands.LONG_FUEL_TRIM_1
        self._commands['LONG_O2_TRIM_B1'] = obd.commands.LONG_O2_TRIM_B1
        self._commands['SHORT_FUEL_TRIM_1'] = obd.commands.SHORT_FUEL_TRIM_1
        self._commands['SHORT_O2_TRIM_B1'] = obd.commands.SHORT_O2_TRIM_B1

        self._connection = obd.OBD()

        #if self._connection.status() != obd.OBDStatus.CAR_CONNECTED:
        #    raise Exception("No connection")

    def read_record(self):
        current_record = dict()
        current_record['TIME_MS'] = round(time.time() * 1000)
        #if self._connection.status() != obd.OBDStatus.CAR_CONNECTED:
        #    raise Exception("No connection")
        for key, query in self._commands.items():
            if query is not None:
                current_record[key] = self._connection.query(query)

        return current_record

    def dict_to_csv_line(self, data):
        csv_string = ""
        for key, val in data.items():
            csv_string = csv_string + f"{val},"

        return csv_string[:-1]

    def dict_to_csv_header(self, data):
        csv_string = ""
        for key, val in data.items():
            csv_string = csv_string + f"{key},"
        return csv_string[:-1]

    def star_logging(self):
        with open(self._filename, "w") as csv_file:
            csv_file.write(f"{self.dict_to_csv_header(self._commands)}\n")
            while True:
                time.sleep(self._refresh_rate_ms/1000)
                record = self.read_record()
                csv_string = self.dict_to_csv_line(record)
                print(csv_string)
                csv_file.write(f"{csv_string}\n")

def create_filename(is_lpg):
    now = datetime.now()
    date_part = now.strftime("%y_%m_%d__%H_%M_%S")
    fuel_type = "BEN"
    if is_lpg:
        fuel_type = "LPG"
    return f"recording_{date_part}_{fuel_type}.csv"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--lpg", action="store_true")

    args = parser.parse_args()

    obd_logger = ObdLogger(create_filename(args.lpg), 500)
    obd_logger.star_logging()
