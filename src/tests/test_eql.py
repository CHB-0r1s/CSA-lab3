from .. import *


def test_eql_1():
    program = "( var a ( - 43 1 ) ) ( = 42 a )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(MAX_STR_LEN * 7, ["H", "i", TERMINATOR], data)
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
        assert cu.data_path.data_memory[sp] == 1


def test_eql_2():
    program = "( var a ( - 43 1 ) ) ( = 43 a )"
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
        assert cu.data_path.data_memory[sp] == 0
