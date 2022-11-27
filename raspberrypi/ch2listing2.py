from gpiozero import LED
from signal import pause

red = LED(25) # https://gpiozero.readthedocs.io/en/stable/api_output.html
red.blink()
#red.off()

pause()