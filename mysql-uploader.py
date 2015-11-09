#!/usr/bin/python

import MySQLdb
import sys
import time
import signal
import argparse
import getpass


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed,
    # and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    db.commit()
    cursor.close()
    sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == '__main__':
    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    parser = argparse.ArgumentParser(description='Inserts temperature data to a MySQL database')
    parser.add_argument('--host', default='127.0.0.1', help='Hostname or IP address to connect to (default: %(default)s)')
    parser.add_argument('-u', '--user', default='root', help='Username (default: %(default)s)')
    parser.add_argument('-p', '--password')
    parser.add_argument('-f', '--file', default='STDIN', help='File to read from (default: %(default)s)')
    parser.add_argument('database', help='Database to use')
    args = parser.parse_args()

    if args.password == None:
        args.password = getpass.getpass()

    db = MySQLdb.connect(args.host, args.user, args.password, args.database)
    cursor = db.cursor()
    print 'Connected to', args.database, 'database on', args.user, '@', args.host

    if args.file == 'STDIN':
        file = sys.stdin
    else:
        file = args.file

    while True:
        # where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(1)
            # file.seek(where)
        else:
            line = line.rstrip()
            line = line.replace(' ', ',')
            data = line.split(',')
            # print data
            cursor.execute("INSERT INTO temperature \
                            (datetime, channel, sid, rid, temperature, humidity, low_battery, button_pressed) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",data)
            db.commit()
