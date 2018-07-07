import io
#from time import sleep
import serial


BAUDRATE = 9600 # default baudrate
arduinos = {"COM3": {"baudrate": 19200, "readyline": "Hello!\n"}}


def arduino_serial(port, baudrate=BAUDRATE):
    """Open serial port and return io.TextIOWrapper instance"""
    ser = serial.Serial(port, baudrate)
    ser.timeout = 1 # timeout required to prevent readline() blocking forever
    sio = io.TextIOWrapper(ser,
                           encoding="ASCII",
                           line_buffering=True, # no flush() required
                           write_through=True)
    return sio


def wait_for_line(iowrapper, line_to_wait_for=""):
    found = False
    while True:
        line = iowrapper.readline()
        if line:
            if line == line_to_wait_for:
                found = True
            elif line_to_wait_for == "":
                found = True
        if found:
            return line


for com_port in arduinos:
    baudrate = arduinos[com_port].get("baudrate", BAUDRATE)
    readyline = arduinos[com_port].get("readyline", "")

    # open serial port
    ser = arduino_serial(com_port, baudrate)

    # wait until ready
    line = wait_for_line(ser, readyline)
    print(line, end="")

    ser.write("go\n") # tell arduino to send data continuously

    while True:
        line = ser.readline()
        print(line, end="")
        #ser.write("\n") # request more data
