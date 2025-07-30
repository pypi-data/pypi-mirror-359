# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre(pradeep.garre@teradata.com)
# Secondary Owner: Adithya Avvaru(adithya.avvaru@teradata.com)
#
#
# Version: 1.0
#
# ##################################################################
import teradataml, re
import pandas as pd
import numpy as np
from teradataml import create_context, remove_context, configure, display,\
    UtilFuncs, TeradataConstants, copy_to_sql
from teradataml.dataframe.dataframe import DataFrame as tdml_DataFrame
from teradatamlspk.sql.dataframe import DataFrame
from teradatamlspk.sql.catalog import Catalog
from teradatamlspk.sql.readwriter import DataFrameReader
from teradatamlspk.sql.udf import UDFRegistration
from teradatamlspk.conf import RuntimeConfig
from teradatamlspk.sql.utils import SQLquery
from teradatamlspk.sql.types import StructType, Row
from teradatamlspk.sql.constants import SPARK_TO_TD_TYPES, SQL_NAME_TO_SPARK_TYPES
from teradatasqlalchemy.types import BYTEINT, TIMESTAMP, DECIMAL

display.max_rows = 20

class TeradataSession:

    catalog = Catalog()
    conf = RuntimeConfig()

    @property
    def version(self):
        return configure.database_version

    @property
    def teradataContext(self):
        from teradatamlspk import TeradataContext
        return TeradataContext()
    
    @property
    def _jsparkSession(self):
        """ Returns the TeradataSession """
        return self

    class Builder:

        def config(self, key=None, value=None, conf=None, map=None):
            TeradataSession.conf = conf if conf else RuntimeConfig()
            return self

        def enableHiveSupport(self):
            return self

        def getOrCreate(self, **kwargs):
            create_context(**kwargs)
            return TeradataSession()

        def master(self, master):
            return self

        def remote(self, url):
            return self

        def appName(self, name):
            return self

        def create(self, **kwargs):
            create_context(**kwargs)
            return TeradataSession()

    builder = Builder()

    def _parse_ddl_schema(self, ddl_str):
        """
        :param ddl_str: DDL string defining the schema. example: "name STRING, age INT, salary FLOAT"
        :return: Tuple of column names and a mapping of column names to Teradata data types.
        Example
        -------
        >>> columns, type_map = session._parse_ddl_schema("name STRING, age INT, salary FLOAT")
        >>> print(columns)
        ['name', 'age', 'salary']
        >>> print(type_map)
        {'name': 'VARCHAR', 'age': 'INTEGER', 'salary': 'FLOAT'}
        """
        ddl_str = ddl_str.replace(":", " ")
        fields = (f.strip() for f in ddl_str.split(","))
        columns = []
        type_map = {}
        # Regex: match `col name` or col_name, then type.
        pattern = re.compile(r'(`[^`]+`|\w+)\s+(\w+)', re.UNICODE)
        for field in fields:
            match = pattern.match(field)
            if match:
                col_name = match.group(1)
                # Remove backticks if present.
                if col_name.startswith("`") and col_name.endswith("`"):
                    col_name = col_name[1:-1]
                spark_type = match.group(2).upper()  # e.g., "string" -> "STRING"
                spark_type_class = SQL_NAME_TO_SPARK_TYPES.get(spark_type)
                td_type = SPARK_TO_TD_TYPES.get(type(spark_type_class))
                columns.append(col_name)
                type_map[col_name] = td_type
        return columns, type_map

    def createDataFrame(self, data, schema=None):
        """
        :param data: Vantage Table name.
        :return: teradataml DataFrame.
        """
        type_map, columns = None, None

        if isinstance(data, str):
            return DataFrame(tdml_DataFrame(data))
        
        # If data is a list of Row objects, extract columns and convert to list of dicts.
        if isinstance(data, list) and data and isinstance(data[0], Row):
                columns = list(getattr(data[0], "__fields__", []))
                data = [row.asDict() for row in data]

        # DDL string schema or StructType schema.
        if schema is not None:
            # If schema is a DDL string or StructType, parse it to get columns and type_map.
            if isinstance(schema, str):
                columns, type_map = self._parse_ddl_schema(schema)
            elif isinstance(schema, StructType):
                # Extract column names and types from StructType.
                columns = [field.name for field in schema.fields]
                type_map = {}
                
                for field in schema.fields:
                    # BooleanType special case
                    if field.dataType.__class__.__name__ == "BooleanType":
                        td_type = BYTEINT
                    # If the column is of TIMESTAMP type, then check if it has timezone or not
                    # and assign the corresponding data type.
                    elif field.dataType.__class__.__name__ == "TimestampNTZType":
                        td_type = TIMESTAMP(timezone=True)
                    elif field.dataType.__class__.__name__ == "TimestampType":
                        td_type = TIMESTAMP(timezone=False)
                    # Handle DecimalType with precision and scale.
                    elif field.dataType.__class__.__name__ == "DecimalType":
                        td_type = DECIMAL(field.dataType.precision, field.dataType.scale)
                    
                    else:  
                        td_type_spec = SPARK_TO_TD_TYPES.get(type(field.dataType))
                        td_type = td_type_spec() if isinstance(td_type_spec, type) else td_type_spec
                    type_map[field.name] = td_type
            else:
                columns = schema if isinstance(schema, list) else None

        if isinstance(data, (list, np.ndarray)):
            return DataFrame(tdml_DataFrame(data, types=type_map, columns=columns, index=False))

        if isinstance(data, pd.DataFrame):
            return DataFrame(tdml_DataFrame(data, index=False))
        
    def getActiveSession(self):
        return self

    def active(self):
        return self

    def newSession(self):
        """ Returns the existing TeradataSession """
        return self

    @property
    def readStream(self):
        raise NotImplemented("The API is not supported in Teradata Vantage.")

    def sql(self, sqlQuery, args=None, kwargs=None):
        if args:
            sqlQuery = sqlQuery.format(**args)
        return SQLquery._execute_query(sqlQuery)

    @property
    def read(self):
        return DataFrameReader()
    
    @property
    def udf(self):
        return UDFRegistration(self)

    @staticmethod
    def stop():
        remove_context()
        return

    @staticmethod
    def streams():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def udtf():
        raise NotImplemented("Not supported yet Teradata Vantage.")

    @staticmethod
    def addArtifact():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def addArtifacts():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def copyFromLocalToFs():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def client():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def interruptAll():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def interruptTag():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def interruptOperation():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def addTag():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def removeTag():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def getTags():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def clearTags():
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    @staticmethod
    def table(tableName):
        return DataFrame(tdml_DataFrame(tableName))

    def range(self, start, end=None, step=1, numPartitions = None):
        """ Creates a DataFrame with a range of numbers. """
        from teradataml import td_range
        return DataFrame(td_range(start, end, step))

