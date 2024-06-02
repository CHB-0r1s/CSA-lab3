from src import *


def test_acc_add_number():
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.acc = 10
    dp.alu_right_gate = 15
    dp.signal_left_fetch(SignalsLeftALU.ACC)
    dp.signal_inst_fetch(SignalsALU.ADD)
    assert dp.alu_res == 25


def test_store_to_acc():
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.acc = 10
    dp.alu_right_gate = 5
    dp.signal_inst_fetch(SignalsALU.RG_PASS)
    dp.signal_write()
    assert dp.data_memory[5] == 10


def test_load_to_memory_from_OP():
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.data_memory[5] = 10
    dp.alu_right_gate = 5
    dp.signal_inst_fetch(SignalsALU.RG_PASS)
    dp.signal_read()
    dp.signal_right_fetch(SignalsRightALU.MEM_OUT)
    dp.signal_inst_fetch(SignalsALU.RG_PASS)
    dp.latch_acc_value()
    assert dp.acc == 10


def test_load_to_memory_from_SP():
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.acc = 5
    dp.alu_right_gate = 8
    dp.signal_inst_fetch(SignalsALU.RG_PASS)
    dp.latch_stack_pointer()
    dp.data_memory = [0, 0, 0, 0, 0, 0, 0, 0, 15, 42]
    dp.signal_left_fetch(SignalsLeftALU.SP)
    dp.signal_inst_fetch(SignalsALU.LG_PASS)
    dp.signal_read()
    dp.signal_right_fetch(SignalsRightALU.MEM_OUT)
    dp.signal_inst_fetch(SignalsALU.RG_PASS)
    dp.latch_acc_value()
    assert dp.acc == 15


def test_zero_flag():
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.alu_res = 0
    assert dp.zero()
    dp.alu_res = 1
    assert not dp.zero()


def test_add_instructions_tick_nep():
    instruction = {"opcode": "add", "addr_mod": "nep_addr", "addr": 10}
    dp = DataPath(10, ["H", "i", "T"], [])
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == 10


def test_add_instructions_tick_abs():
    instruction = {"opcode": "add", "addr_mod": "abs_addr", "addr": 9}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.data_memory = [0, 0, 0, 0, 0, 0, 0, 0, 15, 42]
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == 42


def test_sub_instructions_tick_nep():
    print()
    instruction = {"opcode": "sub", "addr_mod": "nep_addr", "addr": 10}
    dp = DataPath(10, ["H", "i", "T"], [])
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == -10


def test_sub_instructions_tick_abs():
    print()
    instruction = {"opcode": "sub", "addr_mod": "abs_addr", "addr": 9}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.data_memory = [0, 0, 0, 0, 0, 0, 0, 0, 15, 42]
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == -42


def test_inc_instructions_tick():
    print()
    instruction = {"opcode": "increment", "addr_mod": "non_addr", "addr": 9}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.acc = 41
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == 42


def test_dec_instructions_tick():
    print()
    instruction = {"opcode": "decrement", "addr_mod": "non_addr", "addr": 9}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.acc = 43
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == 42


def test_add_instructions_tick_abs_tick_count():
    print()
    instruction = {"opcode": "add", "addr_mod": "abs_addr", "addr": 9}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.data_memory = [0, 0, 0, 0, 0, 0, 0, 0, 15, 42]
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.current_tick() == 6


def test_load_instructions_tick_abs():
    print()
    instruction = {"opcode": "load", "addr_mod": "abs_addr", "addr": 9}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.data_memory = [0, 0, 0, 0, 0, 0, 0, 0, 15, 42]
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == 42


def test_load_instructions_tick_nep():
    print()
    instruction = {"opcode": "load", "addr_mod": "nep_addr", "addr": 13}
    dp = DataPath(10, ["H", "i", "T"], [])
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == 13


def test_store_instructions_tick_abs():
    print()
    instruction = {"opcode": "store", "addr_mod": "abs_addr", "addr": 9}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.data_memory = [0, 0, 0, 0, 0, 0, 0, 0, 15, 42]
    dp.acc = 13
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.data_memory[9] == 13


def test_pop_instructions_tick():
    print()
    instruction = {"opcode": "pop", "addr_mod": "non_addr", "addr": None}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.data_memory = [0, 0, 0, 0, 0, 0, 0, 0, 15, 42]
    dp.stack_pointer = 8
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == 15
    assert cu.data_path.stack_pointer == 9


def test_push_instructions_tick():
    print()
    instruction = {"opcode": "push", "addr_mod": "non_addr", "addr": None}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.data_memory = [0, 0, 0, 0, 0, 0, 0, 0, 15, 42]
    dp.stack_pointer = 8
    dp.acc = 13
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.data_memory[7] == 13
    assert cu.data_path.stack_pointer == 7


def test_jump_instructions_tick():
    print()
    instruction = {"opcode": "jump", "addr_mod": "non_addr", "addr": 5}
    dp = DataPath(10, ["H", "i", "T"], [])
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.program_counter == 5


def test_jump_if_zero_instructions_tick():
    print()
    instruction = {"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": 5}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.alu_res = 0
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.program_counter == 5


def test_jump_if_not_zero_instructions_tick():
    print()
    instruction = {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": 5}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.alu_res = 5
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.program_counter == 5


def test_hlt_instructions_tick():
    instruction = {"opcode": "halt", "addr_mod": "non_addr", "addr": None}
    dp = DataPath(10, ["H", "i", "T"], [])
    cu = ControlUnit([instruction], dp)
    try:
        cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)


def test_execute_program_1():
    instruction_0 = {"opcode": "load", "addr_mod": "nep_addr", "addr": 12}
    instruction_1 = {"opcode": "sub", "addr_mod": "nep_addr", "addr": 10}
    instruction_2 = {"opcode": "decrement", "addr_mod": "non_addr", "addr": None}
    instruction_3 = {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": 2}
    instruction_4 = {"opcode": "halt", "addr_mod": "non_addr", "addr": None}
    instructions = [instruction_0, instruction_1, instruction_2, instruction_3, instruction_4]
    dp = DataPath(10, ["H", "i", "T"], [])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.acc == 0


def test_execute_program_4():
    instructions = [
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "2"},
        {"opcode": "add", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "add", "addr_mod": "tos_addr", "addr": None},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "3"},
        {"opcode": "add", "addr_mod": "tos_addr", "addr": None},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "add", "addr_mod": "tos_addr", "addr": None},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "halt", "addr_mod": "non_addr", "addr": None},
    ]

    dp = DataPath(10, ["H", "i", " ", "W", "!", "T"], [])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.acc == 8


def test_execute_program_5():
    print("\n")
    instructions = [
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "2"},
        {"opcode": "sub", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "add", "addr_mod": "tos_addr", "addr": None},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "3"},
        {"opcode": "sub", "addr_mod": "tos_addr", "addr": None},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "add", "addr_mod": "tos_addr", "addr": None},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "halt", "addr_mod": "non_addr", "addr": None},
    ]

    dp = DataPath(10, ["H", "i", " ", "W", "!", "T"], [])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.acc == 2


def test_execute_program_eq():
    print("\n")
    instructions = [
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "sub", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": 4},
        {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": 6},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": 1},
        {"opcode": "jump", "addr_mod": "non_addr", "addr": 7},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": 0},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "halt", "addr_mod": "non_addr", "addr": None},
    ]

    dp = DataPath(10, ["H", "i", " ", "W", "!", "T"], [])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.data_memory[cu.data_path.stack_pointer] == 1


def test_execute_program_not_eq():
    print("\n")
    instructions = [
        {"opcode": "load", "addr_mod": "nep_addr", "addr": "1"},
        {"opcode": "sub", "addr_mod": "nep_addr", "addr": "2"},
        {"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": 4},
        {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": 6},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": 1},
        {"opcode": "jump", "addr_mod": "non_addr", "addr": 7},
        {"opcode": "load", "addr_mod": "nep_addr", "addr": 0},
        {"opcode": "push", "addr_mod": "non_addr", "addr": None},
        {"opcode": "halt", "addr_mod": "non_addr", "addr": None},
    ]

    dp = DataPath(10, ["H", "i", " ", "W", "!", "T"], [])
    cu = ControlUnit(instructions, dp)
    try:
        while True:
            cu.decode_and_execute_instruction()
    except Exception as e:
        assert isinstance(e, StopIteration)
        assert cu.data_path.data_memory[cu.data_path.stack_pointer] == 0


def test_input_buffer_latch():
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.signal_left_fetch(SignalsLeftALU.INPUT)
    dp.signal_inst_fetch(SignalsALU.LG_PASS)
    dp.latch_acc_value()
    dp.alu_res = 5
    dp.signal_write()
    assert dp.data_memory[5] == 72


def test_output_buffer_latch():
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.signal_left_fetch(SignalsLeftALU.INPUT)
    dp.signal_inst_fetch(SignalsALU.LG_PASS)
    dp.latch_acc_value()
    dp.signal_output_write()
    assert dp.output_buffer[0] == "H"


def test_in_instructions_tick():
    instruction = {"opcode": "input", "addr_mod": "non_addr", "addr": 11}
    dp = DataPath(10, ["H", "i", "T"], [])
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.acc == 72


def test_out_instructions_tick():
    instruction = {"opcode": "output", "addr_mod": "non_addr", "addr": 11}
    dp = DataPath(10, ["H", "i", "T"], [])
    dp.acc = 72
    cu = ControlUnit([instruction], dp)
    cu.decode_and_execute_instruction()
    assert cu.data_path.output_buffer[0] == "H"
