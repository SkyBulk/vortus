# Global variables to access data. This will act as an in memory DB.

class VortusStateDB():

    def __init__(self):
        self.collections = {}

    def create_collection(self, name):
        self.collections[name] = []

    def get_collection(self, name):
        return self.collections[name]

    def list(self, col_name):
        return self.collections[col_name]

    def add_to_collection(self, col_name, item):
        self.collections[col_name].append(item)

    def delete_by_criteria(self, col_name, fn):
        for item in self.collections[col_name].copy():
            if fn(item):
                self.collections[col_name].remove(item)

VortusState = VortusStateDB()