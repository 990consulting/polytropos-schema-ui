"""
simple static class for convenient work with data types

You can easily add new types and icons here.

"""


class TypeManager(object):
    collections = ["Folder", "List", "KeyedList"]
    primitives = ["Text", "Integer", "Decimal", "Currency", "Date", "Unary", "Binary"]
    type_icon_dictionary = {
        "Folder": 'fa5s.folder',
        "List": 'fa5s.server',
        "KeyedList": 'fa5s.sitemap',
        "Text": 'fa5s.font',
        "Integer": 'fa5s.superscript',
        "Currency": 'fa5s.money-bill-alt',
        "Date": 'fa5s.calendar',
        "Binary": 'fa5s.balace-scale',
        "Unary": 'fa5s.check-circle',
        "Decimal ": 'fa5s.file',
        "Float": 'fa5s.file'
    }

    @staticmethod
    def get_types_list(value_type):
        if value_type in TypeManager.collections:
            return TypeManager.collections
        else:
            return TypeManager.primitives
