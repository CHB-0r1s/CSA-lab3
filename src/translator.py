#!/usr/bin/python3
import sys

from src import write_code

MAX_STR_LEN = 5
TERMINATOR = "\0"
LAST_ALLOC_SPACE = 0


class CString:
    name: str
    start_addr: int
    end_addr: int
    len_of: int

    def __init__(self, name, start_addr, len_of):
        self.name = name
        self.start_addr = start_addr
        self.len_of = len_of
        self.end_addr = start_addr + len_of - 1


def translate(expr, data):
    expr = expr.replace("\n", " ")  # 0
    s_eval = expr.replace("(", "[")  # 1
    s_eval = s_eval.replace(")", "]")  # 2
    s_eval = s_eval.replace(" ", "', '")  # 3
    s_eval = s_eval.replace("'[', ", "[")  # 4
    s_eval = s_eval.replace(", ']'", "]")  # 5
    s_eval = s_eval.replace("[', ", "[")  # 6
    s_eval = s_eval.replace(", ']", "]")  # 7
    print(s_eval)
    terms = eval(s_eval)
    print(terms)

    asm = []

    variables_primitives = {}
    variables_str = {}
    allocated_str = {"a": CString("a", 0, 3)}

    def static_mem_alloc(memory: list, size: int) -> int:
        pointer_to_start = len(memory)
        for cell_i in range(size):
            memory += [0]
        return pointer_to_start

    def f(terms):
        global LAST_ALLOC_SPACE
        if isinstance(terms, list):
            head = terms[0]
            print(head)
            match head:
                case "put_prim":  # (put_prim primitive) -> status 1
                    if not isinstance(terms[1], list):
                        assert isinstance(terms[1], str), "put_prim: Неверный тип терма"

                        if terms[1].strip("'\"") in variables_primitives.keys():
                            primitive = variables_primitives[terms[1].strip("'\"")]
                            asm.append(
                                {"opcode": "load", "addr_mod": "abs_addr", "addr": primitive, "term": "put_prim"}
                            )
                            asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11, "term": "put_prim"})
                        else:
                            raise NotImplementedError("Доделай пут чар через аски код или через символ")

                    else:
                        terms[1] = f(terms[1])
                        assert terms[1] == "$"

                        asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "put_prim"})
                        asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11, "term": "put_prim"})

                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "put_prim"})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "put_prim"})

                    return "$"

                case "get_prim":  # (get_prim) -> primitive
                    asm.append({"opcode": "input", "addr_mod": "non_addr", "addr": 11, "term": "get_prim"})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "get_prim"})
                    return "$"

                case "load_prim":  # (load_prim address) -> primitive
                    asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": int(terms[1]), "term": "load_prim"})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "load_prim"})

                case "store_prim":  # (store_prim primitive address) -> status 1
                    if terms[2].strip("'\"") in variables_primitives.keys():
                        address = variables_primitives[terms[2]]
                        asm.append(
                            {
                                "opcode": "load",
                                "addr_mod": "abs_addr",
                                "addr": address,
                                "term": "store_prim",
                                "comment": "push variable addr",
                            }
                        )
                        asm.append(
                            {
                                "opcode": "push",
                                "addr_mod": "non_addr",
                                "addr": None,
                                "term": "store_prim",
                                "comment": "push variable addr",
                            }
                        )

                    if terms[1].isdigit():
                        asm.append(
                            {"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]), "term": "store_prim"}
                        )
                    elif terms[1].strip("'\"") in variables_primitives.keys():
                        address = variables_primitives[terms[1]]
                        asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": address, "term": "store_prim"})
                        print(variables_primitives)
                    if terms[2].strip("'\"") in variables_primitives.keys():
                        asm.append({"opcode": "store", "addr_mod": "con_tos_addr", "addr": None, "term": "store_prim"})
                    else:
                        asm.append(
                            {"opcode": "store", "addr_mod": "abs_addr", "addr": int(terms[2]), "term": "store_prim"}
                        )

                    asm.append(
                        {
                            "opcode": "load",
                            "addr_mod": "nep_addr",
                            "addr": 1,
                            "term": "var",
                            "comment": "return 1 if all ok",
                        }
                    )
                    asm.append(
                        {
                            "opcode": "push",
                            "addr_mod": "non_addr",
                            "addr": None,
                            "term": "var",
                            "comment": "return 1 if all ok",
                        }
                    )

                    return "$"

                case "lisp_read":  # (lisp_read)
                    str_addr = LAST_ALLOC_SPACE
                    log = open("C:\\Users\\Борис\\PycharmProjects\\pythonProject2\\src\\tests\\log.txt", mode="a")
                    print(f"START ADDRESS: {str_addr}", file=log)
                    log.close()
                    f(
                        (
                            ["var", "start_string_address", str(str_addr)],
                            ["var", "char", "0"],
                            [
                                "while",
                                ["<", "1", "char"],
                                [
                                    ["var", "char", ["get_prim"]],
                                    ["store_prim", "char", "start_string_address"],
                                    ["var", "start_string_address", ["+", "1", "start_string_address"]],
                                ],
                            ],
                        )
                    )
                    asm.append(
                        {
                            "opcode": "load",
                            "addr_mod": "nep_addr",
                            "addr": str_addr,
                            "term": "lisp_read",
                            "comment": "return init memory for string",
                        }
                    )
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "lisp_read"})

                    return "$"

                case "read":
                    str_addr = LAST_ALLOC_SPACE
                    asm.append(
                        {
                            "opcode": "load",
                            "addr_mod": "nep_addr",
                            "addr": str_addr,
                            "term": "read",
                            "comment": "Init memory for string",
                        }
                    )
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "read"})
                    asm.append({"opcode": "input", "addr_mod": "non_addr", "addr": 11, "term": "read"})
                    asm.append({"opcode": "store", "addr_mod": "con_tos_addr", "addr": None, "term": "read"})
                    asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": ord(TERMINATOR), "term": "read"})
                    asm.append({"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": len(asm) + 5, "term": "read"})
                    asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "read"})
                    asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": 1, "term": "read"})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "read"})
                    asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) - 7, "term": "read"})
                    asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "read"})

                    asm.append(
                        {
                            "opcode": "load",
                            "addr_mod": "nep_addr",
                            "addr": str_addr,
                            "term": "read",
                            "comment": "Return string addr",
                        }
                    )
                    asm.append(
                        {
                            "opcode": "push",
                            "addr_mod": "non_addr",
                            "addr": None,
                            "term": "read",
                            "comment": "Return string addr",
                        }
                    )

                    return "$"

                case "var_input":
                    size = int(terms[1])
                    name = terms[2]
                    if name not in variables_str:
                        str_pointer = static_mem_alloc(data, size)
                        LAST_ALLOC_SPACE = str_pointer
                        variables_str[name] = str_pointer
                        allocated_str[name] = CString(name, str_pointer, size)
                    else:
                        LAST_ALLOC_SPACE = variables_str[name]

                    if isinstance(terms[3], list):
                        terms[3] = f(terms[3])

                    asm.append(
                        {
                            "opcode": "load",
                            "addr_mod": "nep_addr",
                            "addr": 1,
                            "term": "var_input",
                            "comment": "return 1 if all ok",
                        }
                    )
                    asm.append(
                        {
                            "opcode": "push",
                            "addr_mod": "non_addr",
                            "addr": None,
                            "term": "var_input",
                            "comment": "return 1 if all ok",
                        }
                    )
                    return "$"

                case "var":
                    if isinstance(terms[2], str):
                        if terms[1].strip("'\"") not in variables_primitives.keys():
                            if terms[2].strip("'\"").isdigit() or terms[2].strip("'\"") in variables_primitives.keys():
                                prim_pointer = static_mem_alloc(data, 1)
                                LAST_ALLOC_SPACE = prim_pointer
                                name = terms[1]
                                variables_primitives[name] = prim_pointer
                                allocated_str[name] = CString(name, prim_pointer, 1)

                        if terms[2].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "load",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[2]],
                                    "term": "var",
                                    "comment": "Load concrete known value",
                                }
                            )
                            asm.append(
                                {
                                    "opcode": "store",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[1]],
                                    "term": "var",
                                }
                            )
                        else:
                            if not terms[2].strip("'\"").isdigit():
                                str_pointer = static_mem_alloc(data, len(terms[2]) + 1)
                                variables_str[terms[1]] = str_pointer

                                chars = list(terms[2]) + ["\0"]
                                assert TERMINATOR in chars, f"Строка без терминирующего символа '{TERMINATOR}'"

                                for i in range(0, len(chars)):
                                    address = i + str_pointer
                                    cur_char = ord(chars[i])
                                    data[address] = cur_char

                            else:
                                print(data)
                                print(len(data), LAST_ALLOC_SPACE)
                                data[LAST_ALLOC_SPACE] = int(terms[2])

                    if isinstance(terms[2], list):
                        if "read" not in terms[2]:
                            if terms[1].strip("'\"") not in variables_primitives.keys():
                                prim_pointer = static_mem_alloc(data, 1)
                                LAST_ALLOC_SPACE = prim_pointer
                                name = terms[1]
                                variables_primitives[name] = prim_pointer
                                allocated_str[name] = CString(name, prim_pointer, 1)
                            terms[2] = f(terms[2])
                            if terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "var"})
                                asm.append(
                                    {
                                        "opcode": "store",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[1]],
                                        "term": "var",
                                    }
                                )
                        else:
                            terms[2] = f(terms[2])
                            variables_str[terms[1]] = terms[2]
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "var"})

                    asm.append(
                        {
                            "opcode": "load",
                            "addr_mod": "nep_addr",
                            "addr": 1,
                            "term": "var",
                            "comment": "return 1 if all ok",
                        }
                    )
                    asm.append(
                        {
                            "opcode": "push",
                            "addr_mod": "non_addr",
                            "addr": None,
                            "term": "var",
                            "comment": "return 1 if all ok",
                        }
                    )

                case "+":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "load",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[1]],
                                    "term": "+",
                                }
                            )
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1], "term": "+"})
                        if terms[2].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "add",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[2]],
                                    "term": "+",
                                }
                            )
                        else:
                            asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": terms[2], "term": "+"})

                        asm.append(
                            {
                                "opcode": "push",
                                "addr_mod": "non_addr",
                                "addr": None,
                                "term": "+",
                                "comment": "Return sum value",
                            }
                        )
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[2] = f(terms[2])

                            if terms[1].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[1]],
                                        "term": "+",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1], "term": "+"})

                            if terms[1] != "$" and terms[2] == "$":
                                asm.append({"opcode": "add", "addr_mod": "tos_addr", "addr": None, "term": "+"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "+"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])

                            if terms[2].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "add",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[2]],
                                        "term": "+",
                                    }
                                )
                            else:
                                asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": terms[2], "term": "+"})

                            if terms[1] == "$" and terms[2] != "$":
                                asm.append({"opcode": "add", "addr_mod": "tos_addr", "addr": None, "term": "+"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "+"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "+"})
                                asm.append({"opcode": "add", "addr_mod": "tos_addr", "addr": None, "term": "+"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "+"})

                                return "$"
                case "-":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "load",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[1]],
                                    "term": "-",
                                }
                            )
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1], "term": "-"})
                        if terms[2].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "sub",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[2]],
                                    "term": "-",
                                }
                            )
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": terms[2], "term": "-"})

                        asm.append(
                            {
                                "opcode": "push",
                                "addr_mod": "non_addr",
                                "addr": None,
                                "term": "-",
                                "comment": "Return sub value",
                            }
                        )
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[2] = f(terms[2])

                            if terms[1].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[1]],
                                        "term": "-",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1], "term": "-"})

                            if terms[1] != "$" and terms[2] == "$":
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "-"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "-"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])

                            if terms[2].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "sub",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[2]],
                                        "term": "-",
                                    }
                                )
                            else:
                                asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": terms[2], "term": "-"})

                            if terms[1] == "$" and terms[2] != "$":
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "-"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "-"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "-"})
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "-"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "-"})

                                return "$"
                case "=":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "load",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[1]],
                                    "term": "=",
                                }
                            )
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]), "term": "="})
                        if terms[2].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "sub",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[2]],
                                    "term": "=",
                                }
                            )
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": int(terms[2]), "term": "="})

                        asm.append(
                            {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3, "term": "="}
                        )  # 2
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "="})  # 3
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "="})  # 4
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0, "term": "="})  # 5
                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "="})  # 6
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[2] = f(terms[2])

                            if terms[1].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[1]],
                                        "term": "=",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1], "term": "="})

                            if terms[1] != "$" and terms[2] == "$":
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "="})
                                asm.append(
                                    {
                                        "opcode": "jump_if_not_zero",
                                        "addr_mod": "non_addr",
                                        "addr": len(asm) + 3,
                                        "term": "=",
                                    }
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "="})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "="}
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0, "term": "="})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "="})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])

                            if terms[2].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[2]],
                                        "term": "=",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2], "term": "="})

                            if terms[1] == "$" and terms[2] != "$":
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "="})
                                asm.append(
                                    {
                                        "opcode": "jump_if_not_zero",
                                        "addr_mod": "non_addr",
                                        "addr": len(asm) + 3,
                                        "term": "=",
                                    }
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "="})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "="}
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0, "term": "="})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "="})

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "="})
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "="})
                                asm.append(
                                    {
                                        "opcode": "jump_if_not_zero",
                                        "addr_mod": "non_addr",
                                        "addr": len(asm) + 3,
                                        "term": "=",
                                    }
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "="})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "="}
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0, "term": "="})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "="})

                                return "$"
                case "<":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "load",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[1]],
                                    "term": "<",
                                }
                            )
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]), "term": "<"})
                        if terms[2].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "sub",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[2]],
                                    "term": "<",
                                }
                            )
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": int(terms[2]), "term": "<"})

                        asm.append(
                            {"opcode": "jump_if_not_neg", "addr_mod": "non_addr", "addr": len(asm) + 3, "term": "<"}
                        )  # 2
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "<"})  # 3
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "<"})  # 4
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0, "term": "<"})  # 5
                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "<"})  # 6
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[2] = f(terms[2])

                            if terms[1].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[1]],
                                        "term": "<",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1], "term": "<"})

                            if terms[1] != "$" and terms[2] == "$":
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "<"})
                                asm.append(
                                    {
                                        "opcode": "jump_if_not_neg",
                                        "addr_mod": "non_addr",
                                        "addr": len(asm) + 3,
                                        "term": "<",
                                    }
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "<"})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "<"}
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0, "term": "<"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "<"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])

                            if terms[2].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[2]],
                                        "term": "<",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2], "term": "<"})

                            if terms[1] == "$" and terms[2] != "$":
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "<"})
                                asm.append(
                                    {
                                        "opcode": "jump_if_not_neg",
                                        "addr_mod": "non_addr",
                                        "addr": len(asm) + 3,
                                        "term": "<",
                                    }
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "<"})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "<"}
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0, "term": "<"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "<"})

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "<"})
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None, "term": "<"})
                                asm.append(
                                    {
                                        "opcode": "jump_if_not_neg",
                                        "addr_mod": "non_addr",
                                        "addr": len(asm) + 3,
                                        "term": "<",
                                    }
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "<"})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "<"}
                                )
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0, "term": "<"})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "<"})

                                return "$"
                case "if":
                    if isinstance(terms[2], str) and isinstance(terms[3], list):
                        terms[3] = f(terms[3])

                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "if"})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1], "term": "if"})

                        if terms[2] != "$" and terms[3] == "$":
                            asm.append(
                                {"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": len(asm) + 4, "term": "if"}
                            )
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "if"})
                            if terms[2].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[2]],
                                        "term": "if",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2], "term": "if"})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "if"})

                            return "$"

                    if isinstance(terms[2], list) and isinstance(terms[3], str):
                        terms[2] = f(terms[2])

                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "if"})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1], "term": "if"})

                        if terms[2] == "$" and terms[3] != "$":
                            asm.append(
                                {
                                    "opcode": "jump_if_not_zero",
                                    "addr_mod": "non_addr",
                                    "addr": len(asm) + 4,
                                    "term": "if",
                                }
                            )
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "if"})
                            if terms[3].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[3]],
                                        "term": "if",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[3], "term": "if"})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "if"})

                            return "$"

                    if isinstance(terms[2], list) and isinstance(terms[3], list):
                        start_if = len(asm)
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": 0})

                        start_2_addr = len(asm)
                        terms[2] = f(terms[2])
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": 0})
                        finish_2_addr = len(asm) - 1

                        start_3_addr = len(asm)
                        terms[3] = f(terms[3])
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": 0})
                        finish_3_addr = len(asm) - 1

                        asm[start_if]["addr"] = len(asm)

                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "if"})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]), "term": "if"})

                        asm.append(
                            {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": start_2_addr, "term": "if"}
                        )

                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": start_3_addr, "term": "if"})

                        finish = len(asm)
                        asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "if"})
                        asm[finish_2_addr]["addr"] = finish
                        asm[finish_3_addr]["addr"] = finish

                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "if"})

                        return "$"

                    if isinstance(terms[2], str) and isinstance(terms[3], str):
                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "if"})
                        else:
                            if isinstance(terms[1], str):
                                if terms[1] == "$":
                                    asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "if"})
                                else:
                                    if terms[1].strip("'\"") in variables_primitives.keys():
                                        asm.append(
                                            {
                                                "opcode": "load",
                                                "addr_mod": "abs_addr",
                                                "addr": variables_primitives[terms[1]],
                                                "term": "if",
                                            }
                                        )
                                    else:
                                        asm.append(
                                            {
                                                "opcode": "load",
                                                "addr_mod": "nep_addr",
                                                "addr": int(terms[1]),
                                                "term": "if",
                                            }
                                        )

                        if terms[2] != "$" and terms[3] != "$":
                            asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3})
                            if terms[3].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[3]],
                                        "term": "if",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[3], "term": "if"})
                            asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2, "term": "if"})

                            if terms[2].strip("'\"") in variables_primitives.keys():
                                asm.append(
                                    {
                                        "opcode": "load",
                                        "addr_mod": "abs_addr",
                                        "addr": variables_primitives[terms[2]],
                                        "term": "if",
                                    }
                                )
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2], "term": "if"})

                            # asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[2])})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "if"})
                            return "$"
                case "print":
                    if isinstance(terms[1], str):
                        if terms[1].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {
                                    "opcode": "load",
                                    "addr_mod": "abs_addr",
                                    "addr": variables_primitives[terms[1]],
                                    "term": "print",
                                }
                            )
                            asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11, "term": "print"})
                        elif terms[1].strip("'\"") in variables_str.keys():
                            asm.append(
                                {
                                    "opcode": "load",
                                    "addr_mod": "nep_addr",
                                    "addr": variables_str[terms[1]],
                                    "term": "print",
                                }
                            )
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "print"})
                            asm.append({"opcode": "load", "addr_mod": "con_tos_addr", "addr": None, "term": "print"})
                            asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11, "term": "print"})
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": 0, "term": "print"})
                            asm.append(
                                {
                                    "opcode": "jump_if_zero",
                                    "addr_mod": "non_addr",
                                    "addr": len(asm) + 5,
                                    "term": "print",
                                }
                            )
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "print"})
                            asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": 1, "term": "print"})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "print"})
                            asm.append(
                                {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) - 7, "term": "print"}
                            )
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "print"})
                            return "$"

                        else:
                            if terms[1].isdigit():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]), "term": "print"}
                                )
                                asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11, "term": "print"})
                            else:
                                chars = list(terms[1]) + [TERMINATOR]
                                for char in chars:
                                    asm.append(
                                        {"opcode": "load", "addr_mod": "nep_addr", "addr": ord(char), "term": "print"}
                                    )
                                    asm.append(
                                        {"opcode": "output", "addr_mod": "non_addr", "addr": 11, "term": "print"}
                                    )

                    if isinstance(terms[1], list):
                        terms[1] = f(terms[1])
                        asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None, "term": "print"})
                        asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11, "term": "print"})

                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1, "term": "print"})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "print"})
                case "%":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_primitives[terms[1]]}
                            )
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})
                        asm.append({"opcode": "mod", "addr_mod": "nep_addr", "addr": terms[2]})
                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[1] = terms[1]
                            terms[2] = f(terms[2])
                            if terms[1] != "$" and terms[2] == "$":
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})
                                asm.append({"opcode": "mod", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])
                            terms[2] = terms[2]
                            if terms[1] == "$" and terms[2] != "$":
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2]})
                                asm.append({"opcode": "mod", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                                asm.append({"opcode": "mod", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"
                case "while":
                    start_while = len(asm)  # метка первой инструкции while
                    for atoms in terms[2]:
                        f(atoms)
                    if isinstance(terms[1], str):
                        if terms[1].strip("'\"") in variables_primitives.keys():
                            asm.append(
                                {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_primitives[terms[1]]}
                            )
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1])})
                        asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": start_while})
                    if isinstance(terms[1], list):
                        terms[1] = f(terms[1])
                        asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                        asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": start_while})
                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None, "term": "while"})

                    return "$"
        if isinstance(terms, tuple):
            for atom in terms:
                f(atom)

    f(terms)
    asm.append({"opcode": "halt", "addr_mod": "non_addr", "addr": None})
    return asm, data


def main(source, target):
    """Функция запуска транслятора. Параметры -- исходный и целевой файлы."""
    with open(source, encoding="utf-8") as f:
        source = f.read()
    data = [97, 99, 0, 0, 4]
    code, data = translate(source, data)

    write_code(target, code, data)
    print("source LoC:", len(source.split("\n")), "code instr:", len(code))


if __name__ == "__main__":
    _, source, target = sys.argv
    main(source, target)
