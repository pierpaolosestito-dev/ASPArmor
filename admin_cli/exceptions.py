
class SynthaxException(Exception):
    def __init__(self,message):
        super().__init__(f"SynthaxException: {message}")
class SelectableException(Exception):
    def __init__(self, message):
        super().__init__(f"SelectableException: {message}")
class SelectableSynthaxException(SynthaxException):
    def __init__(self, message):
        super().__init__(f"SelectableSynthaxException: {message}")
class CompatibilityException(Exception):
    def __init__(self, message):
        super().__init__(f"CompatibilityException: {message}")
class StructureException(Exception):
    def __init__(self, message):
        super().__init__(f"StructureException: {message}")
class AppArmorException(Exception):
    def __init__(self,message):
        super().__init__(f"AppArmorException: {message}")
class RedundException(Exception):
    def __init__(self,message):
        super().__init__(f"RedundException: {message}")
class SelectException(Exception):
    def __init__(self,message):
        super().__init__(f"SelectException: {message}")


