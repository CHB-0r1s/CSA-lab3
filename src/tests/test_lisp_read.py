from .. import *


def test_read_1():
    program = "( var hello hello ) ( var kirpi4 13 ) ( var_input 3 aboba ( lisp_read ) ) ( var kirpi4 ( + 1 kirpi4 ) )"
    data = [97, 99, 0, 0, 4]
    instructions, data = translate(program, data)
    print(data)
    log = open("C:\\Users\\Борис\\PycharmProjects\\pythonProject2\\src\\tests\\log.txt", mode="a")
    for instruction in instructions:
        print(instruction, end="\n", file=log)
    log.close()
    dp = DataPath(MAX_STR_LEN * 14, ["H", "i", TERMINATOR] + ["H", "i", TERMINATOR], data)
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        print(cu.data_path.data_memory)
        assert cu.data_path.data_memory[5] == ord("h")
        assert cu.data_path.data_memory[6] == ord("e")
        assert cu.data_path.data_memory[7] == ord("l")
