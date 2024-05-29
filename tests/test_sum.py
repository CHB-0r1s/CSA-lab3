from translator import translate, MAX_STR_LEN, TERMINATOR
from machine import ControlUnit, DataPath


def test_sum_1():
    program = "( var a ( + 1 41 ) ) ( + a a )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 3, ["H", "i", TERMINATOR])
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
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 3, ["H", "i", TERMINATOR])
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
