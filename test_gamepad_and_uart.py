from inputs import get_gamepad
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from time import sleep

class Motor:
    __offset = 0
    __position = 0
    __current = 0
        
    def __init__(self, offset, mb_client):
        self.__offset = offset
        self.__mb_client = mb_client
        self.read_data()
        
    def read_data(self):
        if not self.__mb_client.is_socket_open():
            self.__mb_client.connect()
            
        request = client.read_holding_registers(self.__offset, 5, unit=0x01)
        assert(request.function_code < 0x80)        
        self.__position = request.registers[0]
        self.__current = request.registers[2]
        self.__mb_client.close()
        
    def get_position(self):
        return self.__position
    
    def get_current(self):
        return self.__current
    
    def set_position(self, value):
        if (self.__position == value):
            return        
        if not self.__mb_client.is_socket_open():
            self.__mb_client.connect()
        
        while (True):
            request = client.read_holding_registers(self.__offset, 5, unit=0x01)
            if (request.registers[0] == request.registers[1]):
                break
        client.write_register(self.__offset + 3, value=20, unit=0x01)
        client.write_register(self.__offset + 1, value=value, unit=0x01)
        client.write_register(self.__offset + 3, value=5, unit=0x01)
        self.__mb_client.close()
        self.__position = value
        
    def set_current(self, value):
        if (self.__current == value):
            return        
        if not self.__mb_client.is_socket_open():
            self.__mb_client.connect()
        client.write_register(self.__offset + 3, value=value, unit=0x01)
        self.__mb_client.close()
        self.__position = value

client = ModbusClient(method='rtu', port='/dev/ttyS0', baudrate=115200)
#connection = client.connect()

#request = client.read_holding_registers(1, 14, unit=0x01)
#assert(request.function_code < 0x80)   
#print (request)
#print("Motor 1 : ", request.registers)

m1 = Motor(0, client)
m2 = Motor(10, client)
m1.set_position(40)
m2.set_current(5)
gripper = 7
while 1:
    events = get_gamepad()
    for event in events:
        if event.code == 'BTN_MODE':
            value = event.state
            if value == 1:
                print("free")
#                for joint in joints:
#                    joint.free()
        
        if event.code == 'ABS_X':
            value = event.state
            print(event.ev_type, event.code, event.state)
        if event.code == 'ABS_Y':
            print(event.ev_type, event.code, event.state)
        if event.code == 'ABS_RX':
            value = event.state
            print(event.ev_type, event.code, event.state)
            print(m2.get_current())

        if event.code == 'ABS_RY':
            value = event.state
            print(event.ev_type, event.code, event.state)
        if event.code == 'ABS_HAT0Y':            
            value = event.state
            if (value > 0):
                m1.set_position(m1.get_position() + 10)
            if (value < 0):
                m1.set_position(m1.get_position() - 10)
            print(m1.get_position())
        if event.code == 'ABS_HAT0X':
            value = event.state
            #print(event.ev_type, event.code, event.state)
            if (value > 0):
                m2.set_position(m2.get_position() + 10)
            if (value < 0):
                m2.set_position(m2.get_position() - 10)
            print(m2.get_position())
        if event.code == 'BTN_TL':
            if event.state == 1:
                
                gripper = gripper - 1
                if gripper < 7:
                    gripper = 7
                print(gripper)
        if event.code == 'BTN_TR':
            if event.state == 1:
                gripper = gripper + 1
                if gripper > 17:
                    gripper = 17
                print(gripper)
        #calibrate all axis if on point
        if event.code == 'BTN_START':
            if event.state == 1:
                print(event.ev_type, event.code, event.state)
#                for joint in joints:
#                    joint.setAsHome()
        if event.code == 'BTN_SOUTH':
            if event.state == 1:
                print ("no function")
        if event.code == 'BTN_NORTH':
            if event.state == 1:
                print("runProgram")
#                runProgram()
        if event.code == 'BTN_EAST':
            if event.state == 1:
                print(event.ev_type, event.code, event.state)
#                name = input('Name Point (no spaces): ')
#                if name == 'EXIT': break
#                with open("example/points.ini", "a") as pointfile:
#                    for joint in joints:
#                        name += (':'+str(joint.getPosition()))
#                    name +=(':' + str(gripper))
#                    name +=('\n')
#                    pointfile.write(name)
        if event.code == 'BTN_WEST':
            if event.state == 1:
                print(event.ev_type, event.code, event.state)
#                name = input('Go To Point (no spaced): ')
#                moveFilePoint(name)

client.close()
     