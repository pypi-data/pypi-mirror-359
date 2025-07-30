# Version: 0.1.1
import os
import tempfile

class Trueflagger:
    """
    Biblioteca simples para manipulação de flags via arquivos.
    """

    def __init__(self, dir=None):
        self.base_dir = dir or tempfile.gettempdir()

    def _get_flag_path(self, name):
        return os.path.join(self.base_dir, f"{name}.flag")

    def createFlag(self, flagName, value="1"):
        path = self._get_flag_path(flagName)
        with open(path, "w") as f:
            f.write(str(value))

    def readFlag(self, flagName):
        path = self._get_flag_path(flagName)
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return f.read().strip()

    def updateFlag(self, flagName, value):
        path = self._get_flag_path(flagName)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Flag '{flagName}' não existe.")
        with open(path, "w") as f:
            f.write(value)

    def removeFlag(self, flagName):
        path = self._get_flag_path(flagName)
        if os.path.exists(path):
            os.remove(path)
