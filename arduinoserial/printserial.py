import io
#from time import sleep
from itertools import chain

import serial
from boltons.iterutils import unique_iter
from boltons.setutils import IndexedSet


BAUDRATE = 9600 # default baudrate
BAUDRATES = [BAUDRATE, 300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 74880,
             115200, 230400, 250000, 500000, 1000000, 2000000]
#arduinos = {"COM3": {"baudrate": 19200, "readyline": "Hello!\n"}}
arduinos = {"COM3": {}}
#arduinos = {"COM3": {"readyline": "Hello!\n"}}
#arduinos = {"COM3": {"baudrate": 1, "possible_baudrates": [2, 3], "readyline": "Hello!\n"}}
ENCODING = "ASCII"


def arduino_serial(port, baudrate=BAUDRATE):
    """Open serial port and return io.TextIOWrapper instance"""
    ser = serial.Serial(port, baudrate)
    ser.timeout = 1 # timeout required to prevent readline() blocking forever
    sio = io.TextIOWrapper(ser,
                           encoding=ENCODING,
                           line_buffering=True, # no flush() required
                           write_through=True)
    return sio


def wait_for_line(iowrapper, line_to_wait_for=None):
    found = False
    while True:
        line = iowrapper.readline()
        if line:
            if line == line_to_wait_for:
                found = True
            elif not line_to_wait_for: # any line is good enough
                found = True
        if found:
            return line


def bytestr_is_encoding(bytestr, encoding):
    import chardet
    detenc = chardet.detect(bytestr)["encoding"]
    if detenc and detenc.upper() == encoding.upper():
        return True
    return False


def test_baudrate(com_port,
                  firstchoice=BAUDRATE, baudrates=BAUDRATES, encoding=ENCODING):
    """
    Tries to open 'com_port' and read serial messages at various baudrates.
    Returns baudrate where messages are encoded as 'encoding'.
    """
    for baudrate in unique_iter(chain([firstchoice], baudrates)):
        # Open serial port
        ser = arduino_serial(com_port, baudrate)

        # Check serial message encoding
        correct = False
        # often first read is empty.
        # three empty reads in a row probably means totally incompatible rate.
        reads = 0
        maxreads = 3
        while reads < maxreads:
            bytestr = ser.buffer.read(64) # single byte could falsely match
            reads += 1
            if bytestr:
                print("Read some serial data data using baudrate {}"
                      .format(baudrate))
                if bytestr_is_encoding(bytestr, encoding):
                    correct = True
                else:
                    print("Baudrate {} doesn't give us {}."
                          .format(baudrate, encoding))
                break
            else:
                print("Couldn't read anything from serial using baudrate {}"
                      .format(baudrate)) # TODO
                #sleep(1)
        else:
            print("Giving up on baudrate {}".format(baudrate))
        ser.close()
        if correct:
            break
    else:
        # Exhausted baudrates
        print("Exhausted possible baudrates without success.")
        return None
    print("Winner winner chicken dinner baudrate {}".format(baudrate))
    return baudrate


for com_port in arduinos:
    baudrate = arduinos[com_port].get("baudrate", BAUDRATE)
    baudrates = arduinos[com_port].get("possible_baudrates", BAUDRATES)
    baudrates = IndexedSet([baudrate] + baudrates)
    if not baudrate:
        baudrate = baudrates[0]
    readyline = arduinos[com_port].get("readyline")

    baudrate = test_baudrate(com_port, firstchoice=baudrate,
                             baudrates=baudrates)

    # Open serial port
    try:
        ser = arduino_serial(com_port, baudrate)
    except ValueError as e:
        # TODO
        if "Not a valid baudrate: None" in e.args[0]:
            raise ValueError("No valid baudrates could be found in {}"
                             .format(baudrates))
        raise

    # Wait until ready
    line = wait_for_line(ser, readyline)
    print(line, end="")

    ser.write("go\n") # tell arduino to send data continuously

    while True:
        line = ser.readline()
        print(line, end="")
        #ser.write("\n") # request more data
