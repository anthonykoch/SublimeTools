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

### Utils.py

A bunch of random stuff.

## Credit where credit is due

[cuid](https://github.com/necaris/cuid.py) is a package by [necaris](https://github.com/necaris), which is based on Eric Elliots cuid implementation.

[EventEmitter](https://github.com/riga/pymitter) is a package created by [riga](https://github.com/riga)

