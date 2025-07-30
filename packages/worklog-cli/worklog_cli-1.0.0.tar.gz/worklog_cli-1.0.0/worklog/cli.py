from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path
import readline
from worklog.hledger_completer import HledgerCompleter
import subprocess
from arrow import Arrow
from worklog.timeclock import Timeclock
from shutil import copyfile

parser = ArgumentParser()
parser.add_argument("-c", "--config", help="config file", default=Path.home() / ".worklog/worklog.config")
parser.add_argument("-e", "--edit", help="open work log for editing", action="store_true")
parser.add_argument("-a", "--archive", help="save current worklog file at filename")
parser.add_argument("-r", "--report", help="just report worklog", action="store_true")
parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")
opts = parser.parse_args()

config = ConfigParser()
config_defaults = {
    'WORKLOG': {
        'logfile': str(Path.home() / '.worklog' / 'worklog.timeclock'),
        'editor': 'vim'
    }
}

def report(logfile):
    subprocess.run(['hledger', 'bal', '-f', logfile, '--daily', '--begin', 
            Arrow.now().shift(weeks=-1).format('YYYY-MM-DD'), '--average', '--row-total'])

def run():
    configpath = Path(opts.config)
    if configpath.exists():
        if opts.verbose:
            print("Reading config file at {}".format(configpath))
        config.read(configpath)
    else:
        if opts.verbose:
            print("Created config file at {}".format(configpath))
        config.read_dict(config_defaults)
        configpath.parent.mkdir(parents=True, exist_ok=True)
        with configpath.open('w') as cf:
            config.write(cf)
    
    logpath = Path(config['WORKLOG']['logfile'])
    if not logpath.exists():
        if opts.verbose:
            print("Creating worklog file at {}".format(logpath))
        logpath.parent.mkdir(parents=True, exist_ok=True)
        logpath.touch()
    
    if opts.archive:
        copyfile(config['WORKLOG']['logfile'], opts.archive)
        if opts.verbose:
            print("Archived {} as {}".format(cp['WORKLOG']['logfile'], opts.archive))
    if opts.edit:
        subprocess.run("{} {}".format(config['WORKLOG']['editor'], config['WORKLOG']['logfile']), shell=True)
    if opts.report:
        report(logpath)
    if not (opts.archive or opts.edit or opts.report):
        completer = HledgerCompleter(config['WORKLOG']['logfile'])
        readline.set_completer(completer.complete)
        readline.parse_and_bind('set editing-mode vi')
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims('\t\n`~!@#$%^&*()=+[{]}\\|;\'",<>/?')
        tc = Timeclock(config['WORKLOG']['logfile'])
        tc.on_log_out(lambda: report(logpath))
        tc.console()
        print("\n")
