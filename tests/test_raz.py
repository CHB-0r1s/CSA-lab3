from translator import translate, MAX_STR_LEN, TERMINATOR
from machine import ControlUnit, DataPath


def test_raz_1():
    program = "( var a ( - 43 1 ) ) ( - a a )"
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
        assert cu.data_path.data_memory[sp] == 0


def test_sum_4():
    program = "( var a ( - 43 1 ) ) ( - a 10 )"
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
        assert cu.data_path.data_memory[sp] == 32
