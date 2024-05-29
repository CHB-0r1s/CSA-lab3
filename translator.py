#!/usr/bin/python3
import sys

from isa import write_code

MAX_STR_LEN = 20
TERMINATOR = "$"


def translate(expr):
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

    variables_numbers = {}
    variables_str = {}

    def f(terms):
        if isinstance(terms, list):
            head = terms[0]
            print(head)
            match head:
                case "read":
                    str_shift = max(variables_str.values()) if len(variables_str) else 0
                    num_shift = max(variables_numbers.values()) if len(variables_numbers) else 0
                    str_addr = max(str_shift, num_shift) + MAX_STR_LEN + 1
                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": str_addr,
                                "term": "read", "comment": "Init memory for string"})
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

                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": str_addr,
                                "term": "read", "comment": "Return string addr"})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                "term": "read", "comment": "Return string addr"})

                    return "$"
                case "var":
                    if isinstance(terms[2], str):
                        str_shift = max(variables_str.values()) if len(variables_str) else 0
                        num_shift = max(variables_numbers.values()) if len(variables_numbers) else 0

                        if terms[1].strip("\'\"") not in variables_numbers.keys():
                            if terms[2].strip("\'\"").isdigit() or terms[2].strip("\'\"") in variables_numbers.keys():
                                variables_numbers[terms[1]] = max(str_shift, num_shift) + MAX_STR_LEN + 1

                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                        "term": "var", "comment": "Load concrete known value"})
                            asm.append({"opcode": "store", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                        "term": "var"})
                        else:
                            if not terms[2].strip("\'\"").isdigit():
                                str_shift = max(variables_str.values()) if len(variables_str) else 0
                                num_shift = max(variables_numbers.values()) if len(variables_numbers) else 0
                                str_addr = max(str_shift, num_shift) + MAX_STR_LEN + 1
                                variables_str[terms[1]] = str_addr
                                chars = list(terms[2])
                                assert TERMINATOR in chars, f"Строка без терминирующего символа '{TERMINATOR}'"
                                assert len(chars) < MAX_STR_LEN, "Строка слишком большая"

                                for char in chars:
                                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": ord(char),
                                                "term": "var"})
                                    asm.append({"opcode": "store", "addr_mod": "abs_addr", "addr": str_addr,
                                                "term": "var"})
                                    str_addr += 1

                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[2]),
                                            "term": "var"})
                                asm.append(
                                    {"opcode": "store", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                     "term": "var"})

                    if isinstance(terms[2], list):
                        if "read" not in terms[2]:
                            if terms[1].strip("\'\"") not in variables_numbers.keys():
                                str_shift = max(variables_str.values()) if len(variables_str) else 0
                                num_shift = max(variables_numbers.values()) if len(variables_numbers) else 0
                                variables_numbers[terms[1]] = max(str_shift, num_shift) + MAX_STR_LEN + 1
                            terms[2] = f(terms[2])
                            if terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                            "term": "var"})
                                asm.append({"opcode": "store", "addr_mod": "abs_addr",
                                            "addr": variables_numbers[terms[1]], "term": "var"})
                        else:
                            terms[2] = f(terms[2])
                            variables_str[terms[1]] = terms[2]
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                        "term": "var"})

                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                "term": "var", "comment": "return 1 if all ok"})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                "term": "var", "comment": "return 1 if all ok"})

                case "+":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                        "term": "+"})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1],
                                        "term": "+"})
                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "add", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                        "term": "+"})
                        else:
                            asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": terms[2],
                                        "term": "+"})

                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                    "term": "+", "comment": "Return sum value"})
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[2] = f(terms[2])

                            if terms[1].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                     "term": "+"})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1],
                                     "term": "+"})

                            if terms[1] != "$" and terms[2] == "$":
                                asm.append(
                                    {"opcode": "add", "addr_mod": "tos_addr", "addr": None,
                                     "term": "+"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "+"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])

                            if terms[2].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "add", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                     "term": "+"})
                            else:
                                asm.append(
                                    {"opcode": "add", "addr_mod": "nep_addr", "addr": terms[2],
                                     "term": "+"})

                            if terms[1] == "$" and terms[2] != "$":
                                asm.append(
                                    {"opcode": "add", "addr_mod": "tos_addr", "addr": None,
                                     "term": "+"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "+"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append(
                                    {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                     "term": "+"})
                                asm.append(
                                    {"opcode": "add", "addr_mod": "tos_addr", "addr": None,
                                     "term": "+"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "+"})

                                return "$"
                case "-":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                        "term": "-"})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1],
                                        "term": "-"})
                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "sub", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                        "term": "-"})
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": terms[2],
                                        "term": "-"})

                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                    "term": "-", "comment": "Return sub value"})
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[2] = f(terms[2])

                            if terms[1].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                     "term": "-"})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1],
                                     "term": "-"})

                            if terms[1] != "$" and terms[2] == "$":
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "-"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "-"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])

                            if terms[2].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                     "term": "-"})
                            else:
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "nep_addr", "addr": terms[2],
                                     "term": "-"})

                            if terms[1] == "$" and terms[2] != "$":
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "-"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "-"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append(
                                    {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                     "term": "-"})
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "-"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "-"})

                                return "$"
                case "=":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                        "term": "="})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]),
                                        "term": "="})
                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "sub", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                        "term": "="})
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": int(terms[2]),
                                        "term": "="})

                        asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3,
                                    "term": "="})  # 2
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                    "term": "="})  # 3
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                    "term": "="})  # 4
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0,
                                    "term": "="})  # 5
                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                    "term": "="})  # 6
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[2] = f(terms[2])

                            if terms[1].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                     "term": "="})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1],
                                     "term": "="})

                            if terms[1] != "$" and terms[2] == "$":

                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 0,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "="})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])

                            if terms[2].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                     "term": "="})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2],
                                     "term": "="})

                            if terms[1] == "$" and terms[2] != "$":
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 0,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "="})

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append(
                                    {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 0,
                                     "term": "="})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "="})

                                return "$"
                case "<":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                        "term": "<"})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]),
                                        "term": "<"})
                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "sub", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                        "term": "<"})
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": int(terms[2]),
                                        "term": "<"})

                        asm.append({"opcode": "jump_if_not_neg", "addr_mod": "non_addr", "addr": len(asm) + 3,
                                    "term": "<"})  # 2
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                    "term": "<"})  # 3
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                    "term": "<"})  # 4
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0,
                                    "term": "<"})  # 5
                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                    "term": "<"})  # 6
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[2] = f(terms[2])

                            if terms[1].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                     "term": "<"})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1],
                                     "term": "<"})

                            if terms[1] != "$" and terms[2] == "$":
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "jump_if_not_neg", "addr_mod": "non_addr", "addr": len(asm) + 3,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 0,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "<"})

                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])

                            if terms[2].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                     "term": "<"})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2],
                                     "term": "<"})

                            if terms[1] == "$" and terms[2] != "$":
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "jump_if_not_neg", "addr_mod": "non_addr", "addr": len(asm) + 3,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 0,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "<"})

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append(
                                    {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "sub", "addr_mod": "tos_addr", "addr": None,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "jump_if_not_neg", "addr_mod": "non_addr", "addr": len(asm) + 3,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": 0,
                                     "term": "<"})
                                asm.append(
                                    {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                     "term": "<"})

                                return "$"
                case "if":
                    if isinstance(terms[2], str) and isinstance(terms[3], list):
                        terms[3] = f(terms[3])

                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append(
                                {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                 "term": "if"})
                        else:
                            asm.append(
                                {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1],
                                 "term": "if"})

                        if terms[2] != "$" and terms[3] == "$":
                            asm.append(
                                {"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": len(asm) + 4,
                                 "term": "if"})
                            asm.append(
                                {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                 "term": "if"})
                            if terms[2].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                     "term": "if"})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2],
                                     "term": "if"})
                            asm.append(
                                {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                 "term": "if"})

                            return "$"

                    if isinstance(terms[2], list) and isinstance(terms[3], str):
                        terms[2] = f(terms[2])

                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append(
                                {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                 "term": "if"})
                        else:
                            asm.append(
                                {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1],
                                 "term": "if"})

                        if terms[2] == "$" and terms[3] != "$":
                            asm.append(
                                {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 4,
                                 "term": "if"})
                            asm.append(
                                {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                 "term": "if"})
                            if terms[3].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[3]],
                                     "term": "if"})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[3],
                                     "term": "if"})
                            asm.append(
                                {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                 "term": "if"})

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
                            asm.append(
                                {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                 "term": "if"})
                        else:
                            asm.append(
                                {"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]),
                                 "term": "if"})

                        asm.append(
                            {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": start_2_addr,
                             "term": "if"})


                        asm.append(
                            {"opcode": "jump", "addr_mod": "non_addr", "addr": start_3_addr,
                             "term": "if"})

                        finish = len(asm)
                        asm.append(
                            {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                             "term": "if"})
                        asm[finish_2_addr]["addr"] = finish
                        asm[finish_3_addr]["addr"] = finish

                        asm.append(
                            {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                             "term": "if"})

                        return "$"

                    if isinstance(terms[2], str) and isinstance(terms[3], str):
                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append(
                                {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                 "term": "if"})
                        else:
                            if isinstance(terms[1], str):
                                if terms[1] == "$":
                                    asm.append(
                                        {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                         "term": "if"})
                                else:
                                    if terms[1].strip("\'\"") in variables_numbers.keys():
                                        asm.append(
                                            {"opcode": "load", "addr_mod": "abs_addr",
                                             "addr": variables_numbers[terms[1]],
                                             "term": "if"})
                                    else:
                                        asm.append(
                                            {"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]),
                                             "term": "if"})

                        if terms[2] != "$" and terms[3] != "$":
                            asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3})
                            if terms[3].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[3]],
                                     "term": "if"})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[3],
                                     "term": "if"})
                            asm.append(
                                {"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2,
                                 "term": "if"})

                            if terms[2].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]],
                                     "term": "if"})
                            else:
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2],
                                     "term": "if"})

                            # asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[2])})
                            asm.append(
                                {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                 "term": "if"})
                            return "$"
                case "print":
                    if isinstance(terms[1], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]],
                                        "term": "print"})
                            asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11,
                                        "term": "print"})
                        elif terms[1].strip("\'\"") in variables_str.keys():
                            asm.append(
                                {"opcode": "load", "addr_mod": "nep_addr", "addr": variables_str[terms[1]],
                                 "term": "print"})
                            asm.append(
                                {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                 "term": "print"})
                            asm.append(
                                {"opcode": "load", "addr_mod": "con_tos_addr", "addr": None,
                                 "term": "print"})
                            asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11,
                                        "term": "print"})
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": 0,
                                        "term": "print"})
                            asm.append({"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": len(asm) + 5,
                                        "term": "print"})
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                        "term": "print"})
                            asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": 1,
                                        "term": "print"})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None,
                                        "term": "print"})
                            asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) - 7,
                                        "term": "print"})
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                                        "term": "print"})
                            return "$"

                        else:
                            if terms[1].isdigit():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1]),
                                     "term": "print"})
                                asm.append(
                                    {"opcode": "output", "addr_mod": "non_addr", "addr": 11,
                                     "term": "print"})
                            else:
                                assert TERMINATOR in terms[1], f"Строка без терминирующего символа '{TERMINATOR}'"
                                for char in terms[1]:
                                    asm.append(
                                        {"opcode": "load", "addr_mod": "nep_addr", "addr": ord(char),
                                         "term": "print"})
                                    asm.append(
                                        {"opcode": "output", "addr_mod": "non_addr", "addr": 11,
                                         "term": "print"})

                    if isinstance(terms[1], list):
                        terms[1] = f(terms[1])
                        asm.append(
                            {"opcode": "pop", "addr_mod": "nep_addr", "addr": None,
                             "term": "print"})
                        asm.append(
                            {"opcode": "output", "addr_mod": "non_addr", "addr": 11,
                             "term": "print"})

                    asm.append(
                        {"opcode": "load", "addr_mod": "nep_addr", "addr": 1,
                         "term": "print"})
                    asm.append(
                        {"opcode": "push", "addr_mod": "non_addr", "addr": None,
                         "term": "print"})
                case "%":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
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
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1])})
                        asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": start_while})
                    if isinstance(terms[1], list):
                        terms[1] = f(terms[1])
                        asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                        asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": start_while})

        if isinstance(terms, tuple):
            for atom in terms:
                f(atom)

    f(terms)
    asm.append({"opcode": "halt", "addr_mod": "non_addr", "addr": None})
    return asm


def main(source, target):
    """Функция запуска транслятора. Параметры -- исходный и целевой файлы."""
    with open(source, encoding="utf-8") as f:
        source = f.read()

    code = translate(source)

    write_code(target, code)
    print("source LoC:", len(source.split("\n")), "code instr:", len(code))


if __name__ == "__main__":
    # assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    # _, source, target = sys.argv
    main("examples\\prop.txt", "out.txt")
