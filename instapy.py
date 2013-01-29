import imp


def get_module(import_str):
    return imp.load_module(import_str, *imp.find_module(import_str))
