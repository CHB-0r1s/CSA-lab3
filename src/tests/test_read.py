from .. import *


def test_read_1():
    program = "( read )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(40, ["H", "i", TERMINATOR], data)
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)
        assert cu.data_path.data_memory[5] == ord("H")
        assert cu.data_path.data_memory[6] == ord("i")
        assert cu.data_path.data_memory[7] == ord(TERMINATOR)


def test_read_2():
    program = "( var a ( + 1 ( read ) ) )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(40, ["H", "i", TERMINATOR], data)
    print(data)
    cu = ControlUnit(instructions, dp)
    # for instr in instructions:
    #    print(instr, file=open("/out.txt", mode="a"))
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)
        assert cu.data_path.data_memory[5] == 6
        assert cu.data_path.data_memory[6] == ord("i")

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 1


def test_read_3():
    program = "( var_input 3 a ( read ) )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    dp = DataPath(MAX_STR_LEN * 3, ["H", "i", TERMINATOR], data)
    cu = ControlUnit(instructions, dp)
    print(data)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)
        assert cu.data_path.data_memory[5] == ord("H")
        assert cu.data_path.data_memory[6] == ord("i")
        assert cu.data_path.data_memory[7] == ord(TERMINATOR)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 1
