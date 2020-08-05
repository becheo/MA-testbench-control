import subprocess
import time
import datetime

import mysql.connector as mysql
import testbench_control
import testbench_helpers as hlp
import config as cfg

# connect to database
db = mysql.connect(
    host=cfg.host,
    user=cfg.user,
    passwd=cfg.passwd,
    database=cfg.database
)


no_files = 0
wait_seconds = 1  # seconds to wait after one iteration in while loop

# Initialize LEDs on testbench
hlp.init_leds()


while True:
    cursor = db.cursor()

    cursor.execute("SELECT * FROM status")
    status_information = cursor.fetchall()
    db.commit()
    if status_information[0][2] == 'on':
        hlp.illumination('on')
    else:
        hlp.illumination('off')

    cursor.execute("SELECT * FROM queue")
    files = cursor.fetchall()
    db.commit()
    cursor.close()

    if len(files) > 0:
        if no_files > 0:
            print("                         Zeit seit letzter Messung: {}" .format(
                str(datetime.timedelta(seconds=no_files*wait_seconds))))
        no_files = 0

        # output for command prompt
        print("----------------  Neue Messung  -----------------------")
        print("Anzahl der Dateien in der Warteschlange: {}" .format(len(files)))

        print("Folgende Datei wird getestet: {}" .format(files[0][2]))
        # database columns: | queueID | id | filename | add_date |
        queueID_now = files[0][0]
        id_now = files[0][1]
        filename_now = files[0][2]

        testbench_control.run_testbench(filename_now)

        print("Messung beendet - Ergebnisse in Ordner 'results' gespeichert.")
        print("")

        # delete entry from database
        cursor = db.cursor()
        cursor.execute("DELETE FROM queue WHERE queueID = %s", [queueID_now])
        db.commit()
        cursor.close()

        # update status in files table
        cursor = db.cursor()
        cursor.execute(
            "UPDATE files SET status = 'executed' WHERE id = %s", [id_now])
        cursor.execute(
            "UPDATE files SET execution_date = NOW() WHERE id = %s", [id_now])
        db.commit()
        cursor.close()
    else:
        print("Keine Dateien vorhanden, Zeit seit letzter Messung: {}     (zum Beenden: Strg+C)" .format(
            str(datetime.timedelta(seconds=no_files*wait_seconds))), end='\r')
        no_files = no_files + 1

    time.sleep(wait_seconds)
