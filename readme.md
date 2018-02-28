# SublimeTools

Some reusable tools I use when writing sublime plugins.

## Installation

Download or clone the repo into your [packages directory](https://stackoverflow.com/questions/7808452/what-is-the-full-path-to-the-packages-folder-for-sublime-text-2-on-mac-os-lion) with the name `SublimeTools`.

## Included

### Settings.py

A wrapper around sublime.Settings object that automatically updates the underlying settings when they are updated by the user.

### EventEmitter.py

A node like event emitter.

### Exec.py

Contains helpers for executing shell commands, based on sublimes own AsyncProcess class that it uses.

### Node.py

Contains helpers for retrieving the path to the system wide installed node or nvm installed nvm. Currently untested on windows (but it's todo).

### Utils.py

A bunch of random stuff.

## Credit where credit is due

[cuid](https://github.com/necaris/cuid.py) is a package by [necaris](https://github.com/necaris), which is based on Eric Elliots cuid implementation.

[EventEmitter](https://github.com/jfhbrook/pyee) is a package created by [jfhbrook](https://github.com/jfhbrook)
