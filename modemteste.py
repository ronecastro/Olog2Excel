import os 

def enable():
    os.system("netsh interface set interface name='Celular' admin=enabled")

def disable():
    os.system("netsh interface set interface name='Celular' admin=disabled")

enable()
print('enabled command set')