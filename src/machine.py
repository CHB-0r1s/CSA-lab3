#!/usr/bin/python3
import sys
import typing

from src import Opcode
from src import SignalsALU, SignalsLeftALU
from src import SignalsRightALU, SignalsPC, AddrType


class DataPath:
    data_memory_size = None
    data_memory = None
    latched_data = None
    stack_pointer = None
    acc = None
    curr_command: dict = {}
    input_buffer = None
    output_buffer = None
    alu_res = None
    alu_right_gate, alu_left_gate = None, None

    def __init__(self, data_memory_size, input_buffer, data):
        assert data_memory_size > 0, "Data_memory size should be non-zero"
        self.data_memory_size = data_memory_size
        self.data_memory = data + [0] * (data_memory_size - len(data))
        self.data_address = 0
        self.acc = 0
        self.input_buffer: list = input_buffer
        self.output_buffer = []
        self.alu_left_gate, self.alu_right_gate, self.alu_res = 0, 0, 0
        self.stack_pointer = data_memory_size
        self.latched_data = 0

    def signal_write(self):
        self.data_memory[self.alu_res] = self.acc

    def signal_read(self):
        self.latched_data = self.data_memory[self.alu_res]

    def signal_output_write(self):
        symbol = chr(self.acc) if (chr(self.acc).isascii() and self.acc > 34) else str(int(self.acc))
        self.output_buffer.append(symbol)

    def signal_inst_fetch(self, sel: SignalsALU):
        match sel:
            case SignalsALU.INC:
                self.alu_res = self.alu_left_gate + 1
            case SignalsALU.DEC:
                self.alu_res = self.alu_left_gate - 1
            case SignalsALU.ADD:
                self.alu_res = self.alu_left_gate + self.alu_right_gate
            case SignalsALU.SUB:
                self.alu_res = self.alu_left_gate - self.alu_right_gate
            case SignalsALU.MOD:
                self.alu_res = self.alu_left_gate % self.alu_right_gate
            case SignalsALU.LG_PASS:
                self.alu_res = self.alu_left_gate
            case SignalsALU.RG_PASS:
                self.alu_res = self.alu_right_gate

    def signal_left_fetch(self, sel: SignalsLeftALU):
        match sel:
            case SignalsLeftALU.INPUT:
                self.alu_left_gate = ord(self.input_buffer.pop(0))
            case SignalsLeftALU.SP:
                self.alu_left_gate = self.stack_pointer
            case SignalsLeftALU.ACC:
                self.alu_left_gate = self.acc

    def signal_right_fetch(self, sel: SignalsRightALU):
        match sel:
            case SignalsRightALU.OP_COMP:
                self.alu_right_gate = int(self.curr_command["addr"])
            case SignalsRightALU.MEM_OUT:
                self.alu_right_gate = self.latched_data

    def latch_acc_value(self):
        self.acc = self.alu_res

    def latch_return_address(self):
        self.data_address = self.alu_res

    def latch_stack_pointer(self):
        self.stack_pointer = self.alu_res

    def zero(self):
        """Флаг нуля. Необходим для условных переходов."""
        return self.alu_res == 0

    def neg(self):
        return self.alu_res < 0


class ControlUnit:
    program = None
    program_counter = None
    data_path: DataPath = None
    curr_command = {}  # Inst Decoder
    _tick = None

    def __init__(self, program, data_path, log_file):
        self.program = program
        self.program_counter = 0
        self.data_path = data_path
        self._tick = 0
        self.log_file = log_file

    def tick(self, operations: list[tuple]):
        self._tick += 1
        for operation in operations:
            do, log = operation
            do()
            print(log, file=open(log_file, mode="a"))
            # print(log)
            print(self, file=open(log_file, mode="a"))
            # print(self)
            # print("|" +
            #       " ".join([" " * abs(len(str(i)) - 3) + str(i) for i in self.data_path.data_memory]) +
            #       "|", file=open(log_file, mode="a"))
            # print("|" +
            #       " ".join([" " * abs(len(str(i)) - 3) + str(i) for i in range(len(self.data_path.data_memory))]) +
            #       "|", file=open(log_file, mode="a"))

    def current_tick(self):
        return self._tick

    def signal_latch_program_counter(self, sel: SignalsPC):
        match sel:
            case SignalsPC.PC_INC:
                self.program_counter += 1
            case SignalsPC.DP_ADDR:
                self.program_counter = self.data_path.alu_res
            case SignalsPC.INSTR_ADDR:
                self.program_counter = int(self.curr_command["addr"])

    # TODO: print на zero
    def decode_and_execute_control_flow_instruction(self, instr: dict):
        opcode = Opcode(instr["opcode"])

        match opcode:
            case Opcode.HALT:
                raise StopIteration()

            case Opcode.JMP:
                self.signal_latch_program_counter(SignalsPC.INSTR_ADDR)
                self._tick += 1
                print("ADDR -> PC", file=open(log_file, mode="a"))
                return True

            case Opcode.JZ:
                if self.data_path.zero():
                    self.signal_latch_program_counter(SignalsPC.INSTR_ADDR)
                    self._tick += 1
                    print("ADDR -> PC", file=open(log_file, mode="a"))
                else:
                    self.signal_latch_program_counter(SignalsPC.PC_INC)
                    print("PC + 1 -> PC", file=open(log_file, mode="a"))
                return True

            case Opcode.JNZ:
                if not self.data_path.zero():
                    self.signal_latch_program_counter(SignalsPC.INSTR_ADDR)
                    self._tick += 1
                    print("ADDR -> PC", file=open(log_file, mode="a"))
                else:
                    self.signal_latch_program_counter(SignalsPC.PC_INC)
                    print("PC + 1 -> PC", file=open(log_file, mode="a"))
                return True

            case Opcode.JN:
                if self.data_path.neg():
                    self.signal_latch_program_counter(SignalsPC.INSTR_ADDR)
                    self._tick += 1
                    print("ADDR -> PC", file=open(log_file, mode="a"))
                else:
                    self.signal_latch_program_counter(SignalsPC.PC_INC)
                    print("PC + 1 -> PC", file=open(log_file, mode="a"))
                return True

            case Opcode.JNN:
                if not self.data_path.neg():
                    self.signal_latch_program_counter(SignalsPC.INSTR_ADDR)
                    self._tick += 1
                    print("ADDR -> PC", file=open(log_file, mode="a"))
                else:
                    self.signal_latch_program_counter(SignalsPC.PC_INC)
                    print("PC + 1 -> PC", file=open(log_file, mode="a"))
                return True

        return False

    def get_instruction_ticks(self, instruction: dict) -> list[list[tuple[typing.Callable, str]]]:
        opcode = Opcode(instruction["opcode"])
        addr_mod = AddrType(instruction["addr_mod"])

        match opcode:
            case Opcode.ADD:
                if addr_mod == AddrType.ABS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "ADDR -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [
                            (lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.ADD), "ALU_RES = ALU_LG + ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
                if addr_mod == AddrType.NEP_ADDR:
                    return [
                        [
                            (lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "NUM -> ALU_RG"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.ADD), "ALU_RES = ALU_LG + ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
                if addr_mod == AddrType.TOS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.SP), "SP -> ALU_LG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.LG_PASS), "ALU_RES = ALU_LG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.INC), "ALU_RES = SP + 1")],
                        [
                            (lambda: self.data_path.latch_stack_pointer(), "ALU_RES -> SP"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.ADD), "ALU_RES = ALU_LG + ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
            case Opcode.SUB:
                if addr_mod == AddrType.ABS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "ADDR -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [
                            (lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.SUB), "ALU_RES = ALU_LG + ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
                if addr_mod == AddrType.NEP_ADDR:
                    return [
                        [
                            (lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "NUM -> ALU_RG"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.SUB), "ALU_RES = ALU_LG + ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
                if addr_mod == AddrType.TOS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.SP), "SP -> ALU_LG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.LG_PASS), "ALU_RES = ALU_LG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.INC), "ALU_RES = SP + 1")],
                        [
                            (lambda: self.data_path.latch_stack_pointer(), "ALU_RES -> SP"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.SUB), "ALU_RES = ALU_LG + ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
            case Opcode.INC:
                assert addr_mod == AddrType.NON_ADDR, "Неверная адресация, должна быть non_addr"
                return [
                    [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.INC), "ALU_RES = ALU_LG + 1")],
                    [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                ]
            case Opcode.DEC:
                assert addr_mod == AddrType.NON_ADDR, "Неверная адресация, должна быть non_addr"
                return [
                    [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.DEC), "ALU_RES = ALU_LG - 1")],
                    [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                ]
            case Opcode.LOAD:
                if addr_mod == AddrType.ABS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "ADDR -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
                if addr_mod == AddrType.NEP_ADDR:
                    return [
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "NUM -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
                if addr_mod == AddrType.CON_TOS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.SP), "SP -> ALU_LG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.LG_PASS), "ALU_RES = ALU_LG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [(lambda: self.data_path.signal_read(), "READd MEM[ALU]")],
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
            case Opcode.STORE:
                if addr_mod == AddrType.CON_TOS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.SP), "SP -> ALU_LG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.LG_PASS), "ALU_RES = ALU_LG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.signal_write(), "WRITE ACC -> MEM[ALU]")],
                    ]

                return [
                    [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "ADDR -> ALU_RG")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                    [(lambda: self.data_path.signal_write(), "WRITE ACC -> MEM[ALU]")],
                ]
            case Opcode.POP:
                return [
                    [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.SP), "SP -> ALU_LG")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.LG_PASS), "ALU_RES = ALU_LG")],
                    [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.INC), "ALU_RES = SP + 1")],
                    [
                        (lambda: self.data_path.latch_stack_pointer(), "ALU_RES -> SP"),
                        (lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG"),
                    ],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                    [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                ]
            case Opcode.PUSH:
                return [
                    [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.SP), "SP -> ALU_LG")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.DEC), "ALU_RES = SP - 1")],
                    [
                        (lambda: self.data_path.latch_stack_pointer(), "ALU_RES -> SP"),
                        (lambda: self.data_path.signal_write(), "WRITE ACC -> MEM[ALU]"),
                    ],
                ]
            case Opcode.IN:
                return [
                    [(lambda: None, "get IO module port")],
                    [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.INPUT), "INPUT -> ALU_LG")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.LG_PASS), "ALU_RES = ALU_LG")],
                    [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                ]
            case Opcode.OUTPUT:
                return [
                    [(lambda: None, "get IO module port")],
                    [(lambda: self.data_path.signal_output_write(), "ACC -> OUTPUT ")],
                ]
            case Opcode.CLH:
                return [
                    [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.SP), "SP -> ALU_LG")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.LG_PASS), "ALU_RES = ALU_LG")],
                    [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.INC), "ALU_RES = SP + 1")],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.INC), "ALU_RES = SP + 1")],
                    [
                        (lambda: self.data_path.latch_stack_pointer(), "ALU_RES -> SP"),
                        (lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG"),
                    ],
                    [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                    [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                ]
            case Opcode.MOD:
                if addr_mod == AddrType.ABS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "ADDR -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.RG_PASS), "ALU_RES = ALU_RG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [
                            (lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.MOD), "ALU_RES = ALU_LG % ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
                if addr_mod == AddrType.NEP_ADDR:
                    return [
                        [
                            (lambda: self.data_path.signal_right_fetch(SignalsRightALU.OP_COMP), "NUM -> ALU_RG"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.MOD), "ALU_RES = ALU_LG % ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]
                if addr_mod == AddrType.TOS_ADDR:
                    return [
                        [(lambda: self.data_path.signal_left_fetch(SignalsLeftALU.SP), "SP -> ALU_LG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.LG_PASS), "ALU_RES = ALU_LG")],
                        [(lambda: self.data_path.signal_read(), "READ MEM[ALU]")],
                        [(lambda: self.data_path.signal_right_fetch(SignalsRightALU.MEM_OUT), "MEM[ALU] -> ALU_RG")],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.INC), "ALU_RES = SP + 1")],
                        [
                            (lambda: self.data_path.latch_stack_pointer(), "ALU_RES -> SP"),
                            (lambda: self.data_path.signal_left_fetch(SignalsLeftALU.ACC), "ACC -> ALU_LG"),
                        ],
                        [(lambda: self.data_path.signal_inst_fetch(SignalsALU.MOD), "ALU_RES = ALU_LG + ALU_RG")],
                        [(lambda: self.data_path.latch_acc_value(), "ALU_RES -> ACC")],
                    ]

    def decode_and_execute_instruction(self):
        instruction: dict = self.program[self.program_counter]

        self.curr_command = instruction
        self.data_path.curr_command = instruction

        if self.decode_and_execute_control_flow_instruction(instruction):
            return

        operations = self.get_instruction_ticks(instruction)

        for operation in operations:
            self.tick(operation)

        self.signal_latch_program_counter(SignalsPC.PC_INC)

    def __repr__(self):
        """Вернуть строковое представление состояния процессора."""
        state_repr = (
            "TICK: {:3} PC: {:3} ADDR: {:3} MEM_OUT: {} ACC: {} LG_ALU: {:3} RG_ALU: {:3} SP: {:3} ZF: {} |".format(
                self._tick,
                self.program_counter,
                self.data_path.data_address,
                self.data_path.latched_data,
                self.data_path.acc,
                self.data_path.alu_left_gate,
                self.data_path.alu_right_gate,
                self.data_path.stack_pointer,
                int(self.data_path.zero()),
            )
        )

        # instr = self.program[self.program_counter]
        # opcode = instr["opcode"]
        # instr_repr = str(opcode)

        return (
            state_repr
            + "\t"
            + self.program[self.program_counter]["opcode"]
            + (
                ("   " + self.program[self.program_counter]["term"])
                if "term" in self.program[self.program_counter]
                else ""
            )
        )


def simulation(code, input_tokens, data_memory_size, limit, data, log_file):
    data_path = DataPath(data_memory_size, input_tokens, data)
    control_unit = ControlUnit(code, data_path, log_file)
    instr_counter = 0

    try:
        while instr_counter < limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
    except EOFError:
        print("Input buffer is empty!", file=open(log_file, mode="a"))
    except StopIteration:
        print("Well done!", file=open(log_file, mode="a"))

    if instr_counter >= limit:
        print("Limit exceeded!", file=open(log_file, mode="a"))
    print(f"output_buffer: {data_path.output_buffer}", file=open(log_file, mode="a"))
    return "".join(data_path.output_buffer), instr_counter, control_unit.current_tick()


def main(code_file, input_file, log_file):
    data, code = eval(open(code_file).read().replace("null", "None"))
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read().replace("\\0", "\0")
        input_token = []
        for char in input_text:
            input_token.append(char)

    output, instr_counter, ticks = simulation(
        code=code, data=data, input_tokens=input_token, data_memory_size=4000, limit=10000, log_file=log_file
    )

    print("".join(output), file=open(log_file, mode="a"))
    print("instr_counter: ", instr_counter, "ticks:", ticks, file=open(log_file, mode="a"))


if __name__ == "__main__":
    _, code_file, input_file, log_file = sys.argv
    main(code_file, input_file, log_file)
