from translator import translate, MAX_STR_LEN, TERMINATOR
from machine import ControlUnit, DataPath


def test_var_1():
    program = "( var a 1 )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert 1 in cu.data_path.data_memory
        assert cu.data_path.data_memory[MAX_STR_LEN + 1] == 1


def test_var_2():
    try:
        program = "( var a a )"
        instructions = translate(program)
        dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR])
        cu = ControlUnit(instructions, dp)
    except Exception as e:
        assert isinstance(e, AssertionError)


def test_var_3():
    program = f"( var a a{TERMINATOR} )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.data_memory[MAX_STR_LEN + 1] == ord("a")
        assert cu.data_path.data_memory[MAX_STR_LEN + 2] == ord(TERMINATOR)


def test_var_4():
    program = f"( var a {TERMINATOR} )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.data_memory[MAX_STR_LEN + 1] == ord(TERMINATOR)


def test_var_5():
    program = f"( var 1 {TERMINATOR} )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.data_memory[MAX_STR_LEN + 1] == ord(TERMINATOR)


def test_var_6():
    program = f"( var a 1 ) ( var a 10 ) ( + a a )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 20
