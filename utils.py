

def unit_convert(num, unit):
    ret_num = 0
    if unit == '亿':
        ret_num = float(num) * 10000 * 10000
    elif unit == '万':
        ret_num = float(num) * 10000
    elif unit == '千':
        ret_num = float(num) * 1000
    elif unit is None or unit == '':
        ret_num = num
    return ret_num
