from odoo import Command


def get_datas_m2m(m2m):
    """
        Get data to add or sub in m2m ( use in write )
    """
    add = []
    sub = []
    if m2m:
        for _m2m in m2m:
            # Validate 2 formats: From view form and from 'Command' odoo class ( or list of tuples ) 
            command , value = len(_m2m) > 2 and (_m2m[0],_m2m[1]) or _m2m
            if command == Command.LINK:
                add.append(value)
            elif command == Command.UNLINK:
                sub.append(value)
    return add , sub