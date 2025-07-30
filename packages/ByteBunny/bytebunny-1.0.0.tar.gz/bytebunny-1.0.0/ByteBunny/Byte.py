_script_registry = []
class Byte:
    def __init__(self, script_name: str):
        self.script_name = script_name
        _script_registry.append(self)
    @staticmethod
    def get_registered():
        return _script_registry