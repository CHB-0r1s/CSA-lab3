#!/usr/bin/python3
"""Транслятор brainfuck в машинный код.
"""

import sys

from isa import Funcs, Opcode, write_code


def translate(expr):
    expr = expr.replace("\n", " ")
    s_eval = expr.replace("(", "[")  # 1)
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
                    str_addr = str_shift + num_shift + 20
                    print(str_addr)
                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": str_addr, "read": "!"})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                    #
                    asm.append({"opcode": "input", "addr_mod": "non_addr", "addr": 11})
                    asm.append({"opcode": "store", "addr_mod": "con_tos_addr", "addr": None})
                    asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": 0})
                    asm.append({"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": len(asm) + 5})
                    asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                    asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": 1})
                    asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                    asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) - 7})
                    asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                    #
                    return str_addr
                case "var":
                    if isinstance(terms[2], str):
                        str_shift = max(variables_str.values()) if len(variables_str) else 0
                        num_shift = max(variables_numbers.values()) if len(variables_numbers) else 0

                        if terms[1].strip("\'\"") not in variables_numbers.keys():
                            if terms[2].strip("\'\"").isdigit() or terms[2].strip("\'\"") in variables_numbers.keys():
                                variables_numbers[terms[1]] = str_shift + num_shift + 20

                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]]})
                            asm.append({"opcode": "store", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                        else:
                            if not terms[2].strip("\'\"").isdigit():
                                str_shift = max(variables_str.values()) if len(variables_str) else 0
                                num_shift = max(variables_numbers.values()) if len(variables_numbers) else 0
                                str_addr = str_shift + num_shift + 20
                                variables_str[terms[1]] = str_addr
                                chars = list(terms[2])
                                for char in chars:
                                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": ord(char)})
                                    asm.append({"opcode": "store", "addr_mod": "abs_addr", "addr": str_addr})
                                    str_addr += 1

                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[2])})
                                asm.append(
                                    {"opcode": "store", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})

                    if isinstance(terms[2], list):
                        if "read" not in terms[2]:
                            if terms[1].strip("\'\"") not in variables_numbers.keys():
                                str_shift = max(variables_str.values()) if len(variables_str) else 0
                                num_shift = max(variables_numbers.values()) if len(variables_numbers) else 0
                                variables_numbers[terms[1]] = str_shift + num_shift + 20
                            terms[2] = f(terms[2])
                            if terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                                asm.append(
                                    {"opcode": "store", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                        else:
                            terms[2] = f(terms[2])
                            variables_str[terms[1]] = terms[2]

                case "+":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})
                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "add", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]]})
                        else:
                            asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": terms[2]})

                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[1] = terms[1]
                            terms[2] = f(terms[2])
                            if terms[1] != "$" and terms[2] == "$":
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})
                                asm.append({"opcode": "add", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])
                            terms[2] = terms[2]
                            if terms[1] == "$" and terms[2] != "$":
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2]})
                                asm.append({"opcode": "add", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                                asm.append({"opcode": "add", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"
                case "-":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})
                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "sub", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]]})
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": terms[2]})

                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[1] = terms[1]
                            terms[2] = f(terms[2])
                            if terms[1] != "$" and terms[2] == "$":

                                if terms[1].strip("\'\"") in variables_numbers.keys():
                                    asm.append(
                                        {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                                else:
                                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})

                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])
                            terms[2] = terms[2]
                            if terms[1] == "$" and terms[2] != "$":

                                if terms[2].strip("\'\"") in variables_numbers.keys():
                                    asm.append(
                                        {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]]})
                                else:
                                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2]})

                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"
                case "=":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1])})
                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "sub", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]]})
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": int(terms[2])})
                        asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3})  # 2
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1})  # 3
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2})  # 4
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0})  # 5
                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})  # 6
                        return "$"
                    else:
                        if isinstance(terms[1], str) and isinstance(terms[2], list):
                            terms[1] = terms[1]
                            terms[2] = f(terms[2])
                            if terms[1] != "$" and terms[2] == "$":

                                if terms[1].strip("\'\"") in variables_numbers.keys():
                                    asm.append(
                                        {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                                else:
                                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})

                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None})
                                asm.append(
                                    {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3})
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1})
                                asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2})
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"

                        if isinstance(terms[1], list) and isinstance(terms[2], str):
                            terms[1] = f(terms[1])
                            terms[2] = terms[2]
                            if terms[1] == "$" and terms[2] != "$":

                                if terms[2].strip("\'\"") in variables_numbers.keys():
                                    asm.append(
                                        {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]]})
                                else:
                                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2]})

                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None})
                                asm.append(
                                    {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3})
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1})
                                asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2})
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})

                        if isinstance(terms[1], list) and isinstance(terms[2], list):
                            terms[1] = f(terms[1])
                            terms[2] = f(terms[2])
                            if terms[1] == "$" and terms[2] == "$":
                                asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                                asm.append({"opcode": "sub", "addr_mod": "tos_addr", "addr": None})
                                asm.append(
                                    {"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3})
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1})
                                asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2})
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0})
                                asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                                return "$"
                case "<":
                    if isinstance(terms[1], str) and isinstance(terms[2], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})
                        if terms[2].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "sub", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]]})
                        else:
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": terms[2]})
                        asm.append({"opcode": "jump_if_not_neg", "addr_mod": "non_addr", "addr": len(asm) + 3})  # 2
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 1})  # 3
                        asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2})  # 4
                        asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": 0})  # 5
                        asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})  # 6
                        return "$"

                case "if":
                    if isinstance(terms[2], str) and isinstance(terms[3], list):
                        terms[2] = terms[2]
                        terms[3] = f(terms[3])

                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})

                        if terms[2] != "$" and terms[3] == "$":
                            asm.append({"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": len(asm) + 4})
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2]})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                            return "$"

                    if isinstance(terms[2], list) and isinstance(terms[3], str):
                        terms[2] = f(terms[2])
                        terms[3] = terms[3]

                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[1]})

                        if terms[2] == "$" and terms[3] != "$":
                            asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 4})
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[3]})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                            return "$"

                    if isinstance(terms[2], list) and isinstance(terms[3], list):
                        terms[2] = f(terms[2])
                        terms[3] = f(terms[3])

                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                        else:
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1])})

                        if terms[2] == "$" and terms[3] == "$":
                            asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3})
                            asm.append({"opcode": "clean_head", "addr_mod": "nep_addr", "addr": None})
                            asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 3})
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                            return "$"

                    if isinstance(terms[2], str) and isinstance(terms[3], str):
                        if isinstance(terms[1], list):
                            terms[1] = f(terms[1])
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                        else:
                            if isinstance(terms[1], str):
                                if terms[1] == "$":
                                    asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                                else:
                                    asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[1])})

                        if terms[2] != "$" and terms[3] != "$":
                            asm.append({"opcode": "jump_if_not_zero", "addr_mod": "non_addr", "addr": len(asm) + 3})
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[3])})
                            asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) + 2})

                            if terms[2].strip("\'\"") in variables_numbers.keys():
                                asm.append(
                                    {"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[2]]})
                            else:
                                asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": terms[2]})

                            # asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": int(terms[2])})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                            return "$"
                case "print":
                    if isinstance(terms[1], str):
                        if terms[1].strip("\'\"") in variables_numbers.keys():
                            asm.append({"opcode": "load", "addr_mod": "abs_addr", "addr": variables_numbers[terms[1]]})
                        elif terms[1].strip("\'\"") in variables_str.keys():
                            asm.append({"opcode": "load", "addr_mod": "nep_addr", "addr": variables_str[terms[1]]})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                            #
                            asm.append({"opcode": "load", "addr_mod": "con_tos_addr", "addr": None})
                            asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11})
                            asm.append({"opcode": "sub", "addr_mod": "nep_addr", "addr": 0})
                            asm.append({"opcode": "jump_if_zero", "addr_mod": "non_addr", "addr": len(asm) + 5})
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                            asm.append({"opcode": "add", "addr_mod": "nep_addr", "addr": 1})
                            asm.append({"opcode": "push", "addr_mod": "non_addr", "addr": None})
                            asm.append({"opcode": "jump", "addr_mod": "non_addr", "addr": len(asm) - 7})
                            asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                            return

                        else:
                            asm.append(
                                {"opcode": "load",
                                 "addr_mod": "nep_addr",
                                 "addr": int(terms[1]) if terms[1].isdigit() else ord(terms[1].strip("'\""))
                                 }
                            )
                        asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11})
                    if isinstance(terms[1], list):
                        terms[1] = f(terms[1])
                        asm.append({"opcode": "pop", "addr_mod": "nep_addr", "addr": None})
                        asm.append({"opcode": "output", "addr_mod": "non_addr", "addr": 11})
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
    return asm


def main(source, target):
    """Функция запуска транслятора. Параметры -- исходный и целевой файлы."""
    with open(source, encoding="utf-8") as f:
        source = f.read()

    code = translate(source)

    write_code(target, code)
    print("source LoC:", len(source.split("\n")), "code instr:", len(code))


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
