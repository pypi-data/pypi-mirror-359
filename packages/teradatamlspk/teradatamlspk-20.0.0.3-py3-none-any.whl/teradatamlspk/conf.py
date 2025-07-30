from teradataml.utils.utils import execute_sql
from teradataml.dbutils.dbutils import set_session_param, unset_session_param
from teradatamlspk.sql.utils import _pytz_to_teradataml_string_mapper
class TeradataConf:
    def __init__(self):
        self._config = {}

    def contains(self, key):
        return key in self._config

    def getAll(self):
        return [(k, v) for k,v in self._config.items()]

    def set(self, key, value):
        self._config[key] = value
        return self

    def setAll(self, pairs):
        self._config.update(dict(pairs))
        return self

    def get(self, key, defaultValue = None):
        return self._config.get(key, defaultValue)

    def setAppName(self, value):
        return self

    def setExecutorEnv(self, key=None, value=None, pairs=None):
        return self

    def setIfMissing(self, key, value):
        if key not in self._config:
            self._config[key] = value

        return self

    def setMaster(self, value):
        return self

    def setSparkHome(self, value):
        return self

    def toDebugString(self):
        return "\n".join(["{}={}".format(k, v) for k,v in self._config.items()])

    def unset(self, key):
        if key in self._config:
            self._config.pop(key)

class RuntimeConfig(TeradataConf):
    isModifiable = lambda self: False

    def set(self, key, value):
        if key == 'spark.sql.session.timeZone':
            set_session_param('timezone', "\'{}\'".format(_pytz_to_teradataml_string_mapper(value)) if " " not in value else f"'{value}'")

    def unset(self, key):
        if key == 'spark.sql.session.timeZone':
            unset_session_param("timezone")

