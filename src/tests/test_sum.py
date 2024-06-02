from .. import *


def test_sum_1():
    program = "( var a ( + 1 41 ) ) ( + a a )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(MAX_STR_LEN * 3, ["H", "i", TERMINATOR], data)
    cu = ControlUnit(instructions, dp)
    # for instr in instructions:
    #     print(instr, file=open("C:\\Users\\Борис\\PycharmProjects\\pythonProject2\\out.txt", mode="a"))
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 84


def test_sum_2():
    program = "( var a ( + 1 41 ) ) ( + a 10 )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(MAX_STR_LEN * 3, ["H", "i", TERMINATOR], data)
    cu = ControlUnit(instructions, dp)
    # for instr in instructions:
    #     print(instr, file=open("C:\\Users\\Борис\\PycharmProjects\\pythonProject2\\out.txt", mode="a"))
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 52
