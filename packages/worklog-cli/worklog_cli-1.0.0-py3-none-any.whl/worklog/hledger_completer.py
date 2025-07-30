import readline
import csv
import subprocess
import os

# Based on https://stackoverflow.com/questions/7821661/how-to-code-autocompletion-in-python

class HledgerCompleter():
    tempCSV = "temp.csv"

    def __init__(self, logfile):
        self.logfile = logfile
        self.load_options()

    def load_options(self):
        "Queries hledger for the names of accounts"
        try:
            subprocess.run(['hledger', 'bal', '-f', self.logfile, '-o', self.tempCSV])
            with open(self.tempCSV) as csvfile:
                self.options = [account for account, balance in csv.reader(csvfile) 
                        if ':' in account] # Excludes top-level accounts
            os.remove(self.tempCSV)
        except FileNotFoundError:
            self.options = []
        

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None
