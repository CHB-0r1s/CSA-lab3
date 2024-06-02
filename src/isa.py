"""Представление исходного и машинного кода.

Особенности реализации:

- Машинный код сериализуется в список JSON. Один элемент списка -- одна инструкция.
- Индекс списка соответствует:
     - адресу оператора в исходном коде;
     - адресу инструкции в машинном коде.

Пример:

```json
[
    {
        "index": 0,
        "opcode": "jz",
        "arg": 5,
    },
]
```

где:

- `index` -- номер в машинном коде, необходим для того, чтобы понимать, куда делается условный переход;
- `opcode` -- строка с кодом операции (тип: `Opcode`);
- `arg` -- аргумент инструкции (если требуется);
- `term` -- информация о связанном месте в исходном коде (если есть).
"""

import json
from collections import namedtuple
from enum import Enum


class Funcs(str, Enum):
    print_ = "print"
    plus_ = "+"
    minus_ = "-"
    mod_ = "%"
    equal_ = "="
    if_ = "if"
    while_ = "while"
    var_ = "var"


class AddrType(str, Enum):
    NEP_ADDR = "nep_addr"  # непосредственная адресация
    ABS_ADDR = "abs_addr"
    TOS_ADDR = "tos_addr"
    NON_ADDR = "non_addr"
    CON_TOS_ADDR = "con_tos_addr"


class Opcode(str, Enum):
    LOAD = "load"
    STORE = "store"

    INC = "increment"
    DEC = "decrement"
    ADD = "add"
    SUB = "sub"
    MOD = "mod"
    # YAGNI: CMP = "compare"

    JMP = "jump"
    JNZ = "jump_if_not_zero"
    JZ = "jump_if_zero"
    JNN = "jump_if_not_neg"
    JN = "jump_if_neg"

    IN = "input"
    OUTPUT = "output"

    HALT = "halt"

    POP = "pop"
    PUSH = "push"
    CLH = "clean_head"

    def __str__(self):
        return str(self.value)


class SignalsALU(str, Enum):
    ADD = "add"
    SUB = "sub"
    INC = "inc"
    DEC = "dec"
    MOD = "mod"
    RG_PASS = "rg_pass"
    LG_PASS = "lg_pass"


class SignalsLeftALU(str, Enum):
    INPUT = "input"
    SP = "stack_pointer"
    # DA = "data_address"
    ACC = "accumulator"


class SignalsRightALU(str, Enum):
    OP_COMP = "component"
    MEM_OUT = "memory_output"


class SignalsAddressType(str, Enum):
    ALU_ADDR = "address_from_alu_res"
    # DA_ADDR = "data_address"
    SP_ADDR = "stack_pointer"


class SignalsPC(str, Enum):
    DP_ADDR = "data_path_addr"
    PC_INC = "pc+1"
    INSTR_ADDR = "instruction_decoder_addr"


def write_code(filename, code, data):
    """Записать машинный код в файл."""
    with open(filename, "w", encoding="utf-8") as file:
        # Почему не: `file.write(json.dumps(code, indent=4))`?
        # Чтобы одна инструкция была на одну строку.
        file.write("(" + str(data) + ",\n")
        buf = []
        for instr in code:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n ".join(buf) + "])")
