from inputs import get_gamepad
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from time import sleep
from statemachine import StateMachine, State
import threading


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
        assert (request.function_code < 0x80)
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


class RoboArmStateMachine(StateMachine):
    init = State('Init', initial=True)
    up = State('Up')
    down = State('Down')
    left = State('Left')
    right = State('Right')
    idle = State('Idle')
    end = State('End')

    start = init.to(idle)
    go_left = left.from_(up, down, left, idle)
    go_right = right.from_(up, down, right, idle)
    go_up = up.from_(up, left, right, idle)
    go_down = down.from_(down, left, right, idle)
    go_idle = idle.from_(up, down, left, right, idle)
    go_end = end.from_(up, down, left, right, idle, init)

    # def on_start(self):
    #     print('Init!')
    #
    # def on_go_up(self):
    #     print('Go up')
    #
    # def on_enter_up(self):
    #     print('Uppppp!')
    #
    # def on_go_idle(self):
    #     print('Idle!')


def check_game_pad_event(events):
    for event in events:
        # print(event.code)
        return event.code, event.state


def pars_game_pad_event(event):
    event, value = check_game_pad_event(event)

    if event == "ABS_HAT0Y":
        if value == -1:
            return "up"
        elif value == 1:
            return "down"
        else:
            return "idle"

    if event == "ABS_Y":
        if value < -100:
            return "up"
        elif value > 100:
            return "down"
        else:
            return "idle"

    if event == "ABS_HAT0X":
        if value == -1:
            return "left"
        elif value == 1:
            return "right"
        else:
            return "idle"

    if event == "ABS_X":
        if value < -100:
            return "left"
        elif value > 100:
            return "right"
        else:
            return "idle"

    if event == "BTN_SELECT":
        if value == 1:
            return "end"
        else:
            return "idle"


def worker_for_game_pad(sm):
    while 1:
        try:
            val = pars_game_pad_event(get_gamepad())
        except Exception as e:
            print(e)
            sm.go_end()
            break

        try:
            if val == "up":
                sm.go_up()
            elif val == "down":
                sm.go_down()
            elif val == "idle":
                sm.go_idle()
            elif val == "right":
                sm.go_right()
            elif val == "left":
                sm.go_left()
            elif val == "end":
                sm.go_end()
                break
        except Exception as e:
            print(e)


if __name__ == "__main__":
    client = ModbusClient(method='rtu', port='/dev/ttyS0', baudrate=115200)
    # connection = client.connect()

    # request = client.read_holding_registers(1, 14, unit=0x01)
    # assert(request.function_code < 0x80)
    # print (request)
    # print("Motor 1 : ", request.registers)

    # m1 = Motor(0, client)
    # m2 = Motor(10, client)
    # m1.set_position(40)
    # m2.set_current(5)
    ra_sm = RoboArmStateMachine()
    ra_sm.run('start')
    print(ra_sm.current_state)
    gp_key = "idle"
    t_game_pad = threading.Thread(target=worker_for_game_pad, args=(ra_sm, ))
    t_game_pad.start()
    while 1:
        if ra_sm.is_idle:
            pass
        if ra_sm.is_up:
            # m1.set_position(m1.get_position() + 10)
            print(ra_sm.current_state)
        if ra_sm.is_down:
            # curr_pos = m1.get_position()
            # if curr_pos <= 10:
            #     m1.set_position(0)
            # else:
            #     m1.set_position(curr_pos - 10)
            print(ra_sm.current_state)
        if ra_sm.is_left:
            print(ra_sm.current_state)
        if ra_sm.is_right:
            print(ra_sm.current_state)
        if ra_sm.is_end:
            break
        sleep(0.1)

    client.close()
