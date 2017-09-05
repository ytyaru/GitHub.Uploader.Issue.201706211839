#!python3
#encoding:utf-8
class Json2Sqlite(object):
    def __init__(self):
        pass

    def BoolToInt(self, bool_value):
        if not isinstance(bool_value, bool):
            raise Exception('引数はbool型のみ有効ですが、渡された引数の型は {0}, 値は {1} です。'.format(type(bool_value), bool_value))
        if True == bool_value:
            return 1
        else:
            return 0
    def IntToBool(self, int_value):
        if not isinstance(int_value, int):
            raise Exception('引数はint型のみ有効ですが、渡された引数の型は {0}, 値は {1} です。'.format(type(bool_value), bool_value))
        if 0 == int_value:
            return False
        else:
            return True

    def ArrayToString(self, array):
        if not isinstance(array, list):
            raise Exception('引数はlist型のみ有効ですが、渡された引数の型は {0}, 値は {1} です。'.format(type(bool_value), bool_value))
        if None is array or 0 == len(array):
            return None
        ret = ""
        for v in array:
            ret += str(v) + ','
        return ret[:-1]
    def StringToArray(self, string):
        if not isinstance(string, str):
            raise Exception('引数はstr型のみ有効ですが、渡された引数の型は {0}, 値は {1} です。'.format(type(bool_value), bool_value))
        if None is string or 0 == len(string):
            return None
        array = []
        for item in string.split(','):
            if 0 < len(item.strip()):
                array.append(item)
        return array
