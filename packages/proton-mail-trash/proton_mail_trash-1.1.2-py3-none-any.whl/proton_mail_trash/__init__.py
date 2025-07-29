from __future__ import annotations

import sys
from datetime import date, timedelta
from email.parser import HeaderParser
from getpass import getpass
from imaplib import IMAP4

from proton_mail_trash import hydroxide


PORT = 1143


def main() -> None:
    user = input("E-mail: ")
    with hydroxide.run(user):
        password = getpass("Password: ")

        today = date.today()  # noqa: DTZ011 only using naive datetimes
        interval = timedelta(days=30)

        end = today - interval
        criteria = f"(BEFORE {end.strftime('%d-%b-%Y')})"

        box = IMAP4("localhost", PORT)
        box.login(user, password)
        box.select("Trash")
        _typ, data = box.search(None, criteria)
        uids = data[0].split()

        mailparser = HeaderParser()
        to_delete = []
        print("### The following messages will be permanently deleted:")
        for uid in uids:
            _resp, data = box.uid("fetch", uid, "(BODY[HEADER])")
            msg = mailparser.parsestr(data[0][1].decode())
            info = f"{msg['From']}, {msg['Date']}, {msg['Subject']}"
            info = info.replace("\n", "").replace("\r", "")
            print(info)
            to_delete.append(uid)

        if (
            input(
                "### The preceding messages will be permanently deleted. "
                "Continue? (y/n) "
            )
            != "y"
        ):
            print("Abort.")
            sys.exit(1)

        for uid in to_delete:
            print(uid.decode())
            box.store(uid, "+FLAGS", "\\Deleted")

        print("Expunging...")
        box.expunge()
        print("Closing...")
        box.close()
        print("Logging out...")
        box.logout()
        print("Stopping Hydroxide...")
