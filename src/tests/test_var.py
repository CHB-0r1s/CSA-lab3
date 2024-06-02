from .. import *


def test_var_1():
    program = "( var a 1 )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR], data)
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert 1 in cu.data_path.data_memory
        assert cu.data_path.data_memory[-1] == 1


def test_var_2():
    try:
        program = "( var a a )"
        data = [97, 99, 0, 0, 4]
        instructions, data = translate(program, data)
        dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR], data)
        cu = ControlUnit(instructions, dp)
    except Exception as e:
        assert isinstance(e, AssertionError)


def test_var_3():
    program = f"( var a b )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR], data)
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.data_memory[5] == ord("b")
        assert cu.data_path.data_memory[6] == ord(TERMINATOR)


def test_var_4():
    program = f"( var a 1 ) ( var a 10 ) ( + a a )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(MAX_STR_LEN * 2, ["H", "i", TERMINATOR], data)
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 20
