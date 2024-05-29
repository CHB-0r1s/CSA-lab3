from translator import translate, MAX_STR_LEN, TERMINATOR
from machine import ControlUnit, DataPath


def test_if_1():
    program = "( var b 10 ) ( var a ( if ( < 5 b ) b ( + 6 6 ) ) )"
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
        assert cu.data_path.data_memory[sp] == 1

        assert cu.data_path.data_memory[MAX_STR_LEN + 1] == 10
        assert cu.data_path.data_memory[2 * MAX_STR_LEN + 2] == 10


def test_if_2():
    program = "( var a ( - 43 1 ) ) ( = 43 a )"
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