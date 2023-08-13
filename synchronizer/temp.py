from pprint import pprint

strings = ["arg1/arg2/arg3", "arg4/arg5/arg6", "arg1/arg4/arg5", "arg2/arg4/arg5"]

result = {}

for string in strings:
    parts = string.split("/")
    temp_dict = result

    for part in parts[:-1]:
        if part not in temp_dict:
            temp_dict[part] = {}
        temp_dict = temp_dict[part]

    temp_dict[parts[-1]] = {}

pprint(result)