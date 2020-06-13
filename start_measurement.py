import subprocess
import time
import datetime

import mysql.connector as mysql
# import app_helpers
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

# open cmd
# proc = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE)

# activate conda prompt out of cmd
# proc.stdin.write(
#     b"/K C:/Users/Oliver/Anaconda3/Scripts/activate.bat C:/Users/Oliver/Anaconda3\n")

# start the pyhton file running the test
# TODO conda activate virtualenv to the final virtualenv name (maybe: testbench)
# proc.stdin.write(
#     b"cd C:/Users/Oliver/Desktop/Masterarbeit/03_Software/testbench-control && python testbench_control.py\n")

# temporary file link for testing
# proc.stdin.write(
#     b"cd C:/Users/Oliver/Desktop/Masterarbeit/03_Software/z_Tutorials_Beispielprogramme/test-exe && python main.py\n")

# -----------------------------------------------------------------------------------
# possible programm outline:

# check database for entries
# while true:
#   check database for entries
#   get entry with lowest id from database and store filename in variable
#   print data form entry (name of file, id) and seperator(\n ----- \n)
#   run script 'testbench-control.py' with that filename as parameter
#   delete entry that was fetched from database
#   update entries (check database for entries)
#   print number of entries left in database

no_files = 0
wait_seconds = 1  # seconds to wait after one iteration in while loop

# Initialize LEDs on testbench
hlp.init_leds()


while True:
    cursor = db.cursor()

    # TODO überlegen, welche methode hier besser ist: nur erster Eintrag oder alle fetchen
    # result = cursor.execute("SELECT * FROM queue limit 1")
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
        # for i in range(len(files)):
        #     print(files[i])

        print("Folgende Datei wird getestet: {}" .format(files[0]))
        # database columns: | queueID | id | filename | add_date |
        queueID_now = files[0][0]
        id_now = files[0][1]
        filename_now = files[0][2]

        testbench_control.run_testbench(filename_now)

        print("Messung beendet - Ergebnisse in Ordner 'results' gespeichert.")
        print("")

        # delete entry from database
        cursor = db.cursor()
        # TODO überlegen, welche id hier genommen werden soll bzw. auch, ob es die Möglichkeit
        # geben soll einen Test nochmal zu starten, obwohl er schon durchgeführt wurde
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

    # TODO alle 10 min oder so: Kamerabild auf Helligkeit überprüfen, je
    #   nachdem wie hell die LEDs einschalten oder nicht
    #   Strategie fuer das ausschalten ueberlegen

    time.sleep(wait_seconds)
