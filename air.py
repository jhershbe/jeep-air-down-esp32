import machine
import time

stepPeriodMs = 500
relayMap = [12, 13, 14, 25]
relayPins = list(map(lambda io: machine.Pin(io, machine.Pin.OUT), relayMap))
pressurePin = machine.ADC(32, atten=machine.ADC.ATTN_2_5DB)
statusLED = machine.Pin(2, machine.Pin.OUT)
compressedAir = relayPins[0]
ventAir = relayPins[1]

while True:
    presRaw = 0;
    for i in range(256):
        presRaw += pressurePin.read_uv()
    presRaw = presRaw >> 8
    presPSI = (presRaw - 5000000) * 0.00005
    if (presPSI < 0.0):
        presPSI = 0.0
    print("pressure: " + str(presPSI))
    time.sleep_ms(100)
