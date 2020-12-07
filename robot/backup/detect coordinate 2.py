# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 08:46:13 2020

@author: Acr
"""
from pynput import mouse
import threading

def on_click(x, y, button, pressed):
    
    if button == mouse.Button.right:        
        print('{} at {}'.format('Pressed Right Click' if pressed else 'Released Right Click', (x, y)))



def printit():
    threading.Timer(1.0, printit).start()
    #print ("Hello, World!")
    
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()

printit()
