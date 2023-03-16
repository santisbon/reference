from gpiozero import Button

def myfunction():
    print("Button is pressed")
    
button = Button(21)
button.when_pressed = myfunction

#while True:
#    if button.is_pressed:
#        print("Button is pressed")
#    else:
#        #print("Button is not pressed")
#        pass
   
