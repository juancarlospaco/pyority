pyority
=======

**Change CPU and I/O Priorities with Python!**

- CPUs / HDDs Priority Manager
- 200 lines of Python 3 + Qt 5, single-file, 1 Dependency, easy use.
- Inspired by KDE KSysGuard and the dead KNice( http://kde-apps.org/content/show.php?content=66266 )


![screenshot](https://raw.githubusercontent.com/juancarlospaco/pyority/master/temp.jpg)


# Try it !:

```
wget -O - https://raw.githubusercontent.com/juancarlospaco/pyority/master/pyority.py | python3
```

# Install permanently on the system:

```
sudo wget -O /usr/bin/pyority https://raw.githubusercontent.com/juancarlospaco/pyority/master/pyority.py
sudo chmod +x /usr/bin/pyority
pyority
```

# Requisites:

- [Python 3.x](https://www.python.org "Python Homepage")
- [PyQt 5.x](http://www.riverbankcomputing.co.uk/software/pyqt/download5 "PyQt5 Homepage")
- [psutil](https://pypi.python.org/pypi?:action=display&name=psutil#downloads "psutil on pypi")
