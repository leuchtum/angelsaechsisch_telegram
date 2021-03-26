import sys
from .bot import Bot

if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise ValueError("Bitte Schlüssel angeben.")
    elif len(sys.argv) > 2:
        raise ValueError("Zu viele Argumente angegeben.")
    else:
        schlüssel = sys.argv[1]
            
    b = Bot(schlüssel)
    b.arbeite()