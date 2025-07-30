from datetime import datetime

class Timeclock:
    IN = 'i'
    OUT = 'o'
    logout_hook = None

    def __init__(self, logfile):
        self.logfile = logfile
        self.account = None
        self.description = None
        self.loggedIn = False

    def log_in(self, account, description=""):
        self.log(self.IN, account, description)
        self.loggedIn = True

    def log_out(self):
        if self.loggedIn:
            self.log(self.OUT, "")
            self.loggedIn = False
        if self.logout_hook:
            self.logout_hook()

    def on_log_out(self, fn):
        self.logout_hook = fn

    def log(self, activity, account=None, description=None):
        message = [activity, datetime.now().strftime("%Y/%m/%d %H:%M")]
        if account: message.append(account)
        if description: message.append(' ' + description)
        with open(self.logfile, 'a') as logfile:
            logfile.write(' '.join(message) + '\n')

    def console(self):
        try:
            while True:
                if self.account:
                    newAccount = input("Log in to account [{}]: ".format(self.account)).strip()
                    if newAccount:
                        self.account = newAccount
                        self.description = input("Work description: ")
                    else:
                        self.description = input("Work description [{}]: ".format(self.description)) or self.description
                else:
                    self.account = input("Log in to account: ")
                    self.description = input("Work description: ")
                self.log_in(self.account, self.description)
                input("[Enter to log out]")
                self.log_out()
        except KeyboardInterrupt:
            self.log_out()

