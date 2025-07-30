# Worklog

A personal time-tracking system. 

Worklog provides a simple mechanism for logging in and out of accounts which are
billed for time elapsed. The author, a professor, uses it to bill time to
various commitments. Some really are paid hourly (e.g. consulting), but most are
not. The primary use is to track and analyze how time is spent. 

## Installation

Worklog can be easily installed using [pipx](https://pipx.pypa.io/latest/installation/):

    pipx install worklog-cli

You will also need to install [hledger](https://hledger.org/). 

## Usage

If you are just getting started, make a list of the ways you spend time (or at
least those you want to track). If you want to nest accounts, separate them with
colons. For example, here are a few of my accounts:

```
 research:grants
 research:projects
 research:pubs
 research:reading
 research:lab
 teaching:planning
 service:advising
 identity:website
 identity:network
 overhead:email
 overhead:waste
 overhead:admin
```

Now run `work`. You will be asked to log in to an account, and then to enter a
description of the work you are doing. (Accounts can be auto-completed using tab.)

```
% work
Log in to account: academic:code
Work description: Writing the Worklog README
[Enter to log out]
```

Press enter when you finish that work session, and you will be prompted to log
in to another account. Press Control + C when you are finished. That's it!

## Commands

The base command is `work`, which enters a loop for logging in and out of
accounts. There are several other modes available:

- `work --report` shows recent work statistics and quits. 
- `work --edit` opens the current worklog for editing. Sometimes I find I need to
edit the worklog to add a work session or change times (for example, if I forgot
to log out before going to bed). 
- `work --archive` archives the current worklog at the given filename and starts a
new worklog. If you plan to log your work over time, I suggest you keep your log
files in version control. 

## Configuration

Worklog relies on a simple configuration file which will be automatically
created at `~/.worklog/worklog.config` by default. 

```
[WORKLOG]
logfile = /Users/me/.worklog/worklog.timeclock
editor = vim
```

## Formats

Worklog relies on [hledger](https://hledger.org/), a Haskell implementation of
[ledger](https://github.com/ledger/ledger), for double-entry bookkeeping which
regards time as a resource just like money. One main design goal of this system
is a [human-readable ledger format](https://hledger.org/timeclock.html) which
can also be parsed by scripts. 


