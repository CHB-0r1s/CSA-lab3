from translator import translate, MAX_STR_LEN, TERMINATOR
from machine import ControlUnit, DataPath


def test_read_1():
    program = "( read )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)
        assert cu.data_path.data_memory[MAX_STR_LEN + 1] == ord("H")
        assert cu.data_path.data_memory[MAX_STR_LEN + 2] == ord("i")
        assert cu.data_path.data_memory[MAX_STR_LEN + 3] == ord(TERMINATOR)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == MAX_STR_LEN + 1


def test_read_2():
    program = "( var a ( + 1 ( read ) ) )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 3, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    for instr in instructions:
        print(instr, file=open("C:\\Users\\Борис\\PycharmProjects\\pythonProject2\\out.txt", mode="a"))
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)
        assert cu.data_path.data_memory[MAX_STR_LEN + 1] == 2 * (MAX_STR_LEN + 1) + 1
        assert cu.data_path.data_memory[2 * (MAX_STR_LEN + 1)] == ord("H")
        assert cu.data_path.data_memory[2 * (MAX_STR_LEN + 1) + 1] == ord("i")
        assert cu.data_path.data_memory[2 * (MAX_STR_LEN + 1) + 2] == ord(TERMINATOR)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 1


def test_read_3():
    program = "( var a ( read ) )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 3, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    for instr in instructions:
        print(instr, file=open("C:\\Users\\Борис\\PycharmProjects\\pythonProject2\\out.txt", mode="a"))
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)
        assert cu.data_path.data_memory[MAX_STR_LEN + 1] == ord("H")
        assert cu.data_path.data_memory[MAX_STR_LEN + 2] == ord("i")
        assert cu.data_path.data_memory[MAX_STR_LEN + 3] == ord(TERMINATOR)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 1