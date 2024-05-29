from translator import translate, MAX_STR_LEN, TERMINATOR
from machine import ControlUnit, DataPath


def test_print_1():
    program = "( var b 10 ) ( print b )"
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


def test_print_2():
    program = "( var b 10 ) ( print bac$ )"
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
        print(cu.data_path.output_buffer)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 1
        assert not cu.data_path.output_buffer, cu.data_path.output_buffer


def test_print_3():
    program = "( var b 10 ) ( if 1 ( print b ) ( + 0 0 ) )"
    instructions = translate(program)
    dp = DataPath(MAX_STR_LEN * 3, ["H", "i", TERMINATOR])
    cu = ControlUnit(instructions, dp)
    # for instr in instructions:
    #     print(instr, file=open("C:\\Users\\Борис\\PycharmProjects\\pythonProject2\\out.txt", mode="a"))
    print(cu.data_path.output_buffer)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)

        sp = cu.data_path.stack_pointer
        assert cu.data_path.data_memory[sp] == 1
        assert chr(10) in cu.data_path.output_buffer