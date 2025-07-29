from multinut.env import Environment, cast_str, cast_int, cast_float, cast_bool, cast_list, cast_tuple, cast_dict, cast_none_or_str

env = Environment()

print("STRING_VAL:", env.get("STRING_VAL", cast=cast_str))
print("INT_VAL:", env.get("INT_VAL", cast=cast_int))
print("FLOAT_VAL:", env.get("FLOAT_VAL", cast=cast_float))

print("BOOL_1:", env.get("BOOL_1", cast=cast_bool))
print("BOOL_YES:", env.get("BOOL_YES", cast=cast_bool))
print("BOOL_TRUE:", env.get("BOOL_TRUE", cast=cast_bool))
print("BOOL_0:", env.get("BOOL_0", cast=cast_bool))
print("BOOL_NO:", env.get("BOOL_NO", cast=cast_bool))
print("BOOL_FALSE:", env.get("BOOL_FALSE", cast=cast_bool))

print("LIST_CSV:", env.get("LIST_CSV", cast=cast_list))
print("TUPLE_CSV:", env.get("TUPLE_CSV", cast=cast_tuple))
print("DICT_JSON:", env.get("DICT_JSON", cast=cast_dict))

print("NONE_STR:", env.get("NONE_STR", cast=cast_none_or_str))
