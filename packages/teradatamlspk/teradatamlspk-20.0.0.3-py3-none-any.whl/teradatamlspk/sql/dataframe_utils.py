# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pooja Chaudhary(pooja.chaudhary@teradata.com)
# Secondary Owner: Pradeep Garre(pradeep.garre@teradata.com)
#
#
# Version: 1.0
#
# ##################################################################

import warnings
import ast
from inspect import getsource
from teradatamlspk.sql.column import Column
from teradatamlspk.sql.utils import AnalysisException
from teradatamlspk.sql.constants import COMPATIBLE_TYPES
from teradataml.dataframe.sql import _SQLColumnExpression

class DataFrameUtils():

    @staticmethod
    def _tuple_to_list(args, arg_name):
        """
        Converts a tuple of string into list of string and multiple list of strings in a tuple
        to list of strings.

        PARAMETERS:
            args: tuple having list of strings or strings.

        EXAMPLES:
            tuple_to_list(args)

        RETURNS:
            list

        RAISES:
            Value error
        """
        if all(isinstance(value, str) for value in args):
            # Accept only strings in tuple.
            res_list = list(args)
        elif len(args) == 1 and isinstance(args[0], list):
            # Accept one list of strings in tuple.
            res_list = args[0]
        else:
            raise ValueError("'{}' argument accepts only strings or one list of strings".format(arg_name))
        return res_list

    @staticmethod
    def _get_columns_from_tuple_args(args, df_columns):
        """
        Converts a tuple of string, column expression or a list of strings/ column expression in a tuple
        to list of strings.

        PARAMETERS:
            args: tuple having list of strings/ column expression, strings or column expression.
            df_columns: list of column names in the DataFrame.

        EXAMPLES:
            _get_columns_from_tuple_args(args, df_columns)

        RETURNS:
            list
        """
        args = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        columns = []
        for arg in args:
            if arg not in df_columns:
                pass
            else:
                arg = arg if isinstance(arg, str) else arg._tdml_column.name
                columns.append(arg)
        return columns
    
    @staticmethod
    def _udf_col_to_tdml_col(col):
        """
        DESCRIPTION:
            Converts a Column containing UDF expression to teradataml ColumnExpression.

        PARAMETERS:
            col:
                Required Argument.
                Specifies the Column containing UDF expression.
                Types: Column

        RETURNS:
            ColumnExpression
        
        RAISES:
            AnalysisException: If the Column is not present in the DataFrame.

        EXAMPLES:
            >>> _udf_col_to_tdml_col(col)
        """
        args = []
        # Check if the UDF arguments of type Column are present in the DataFrame.
        for arg in col._udf_args:
            if isinstance(arg, Column):
                # Fetch the column name from the Column object.
                col_arg = arg._tdml_column.name
                # If column name is None, it means the Column is not present in the DataFrame and raise an exception.
                if col_arg is None:
                    raise AnalysisException("The derived Column is used by the UDF. Use 'withColumn()' to add the "\
                                            f"derived Column '{arg}' to the DataFrame before using it with UDF.",1)
                # Append the column name to the list of arguments.
                args.append(col_arg)
            else:
                args.append(arg)

        # Check if the UDF is a lambda function and reconstruct it.
        if col._udf and col._udf.__name__ == "<lambda>":
            # Extract the source code of the lambda function.
            col._udf = DataFrameUtils._get_lambda_source_code(col._udf)

        # Converts the Column containing UDF expression to teradataml ColumnExpression.
        from teradatamlspk.sql.utils import _get_tdml_type
        return _SQLColumnExpression(expression=None, udf=col._udf, udf_type=_get_tdml_type(col._udf_type),\
                                    udf_args=args, env_name = col._env_name, delimiter= col._delimiter,\
                                    quotechar=col._quotechar, udf_script = col._udf_script)
    
    @staticmethod
    def _get_lambda_source_code(lambda_udf, lambda_name=None):
        """
        DESCRIPTION:
            Function to extract the source code of a lambda function from 
            the udf() or register() function and reconstruct it.

        PARAMETERS:
            lambda_udf:
                Required Argument.
                Specifies the UDF lambda function.
                Types: function

            lambda_name:
                Optional Argument.
                Specifies the name of the lambda function.
                Types: str
                Default Value: None

        RETURNS:
            Function

        EXAMPLES:
            >>> DataFrameUtils._get_lambda_func_source_code(func)
        """
        # Extract the source code of the lambda function.
        udf_code = getsource(lambda_udf).lstrip()
        # Extract the variable name of the lambda function.
        var_name = udf_code.split('=')[0].strip() if lambda_name is None else lambda_name
        # Get the source code of the lambda function present inside the udf() or register() function.
        # eg. sum = udf(lambda x: x + 1, IntegerType()) -> sum = lambda x: x + 1
        # eg. spark.udf.register("sum", lambda x: x + 1) -> sum = lambda x: x + 1
        tree = ast.parse(udf_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Lambda):
                udf_code = f"{var_name} = {ast.unparse(node)}"
                lambda_udf.__source__ = udf_code
                lambda_udf.__name__ = var_name
                break
        return lambda_udf

    @staticmethod
    def check_value_subset_arg_compatiblity(df, value, column):
        """
        DESCRIPTION:
            Check the type compatibility of value with the DataFrame column.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the value to be checked for compatibility.
                Types: str

            column:
                Required Argument.
                Specifies the column name from the DataFrame.
                Types: str

        EXAMPLES:
            check_value_subset_arg_compatiblity(df, value, column)

        RETURNS:
            bool
        """
        # Check the type of value and assign the compatible type name to val_type.
        val_type = "bool" if isinstance(value, bool) else "int_float" if isinstance(value, (int, float)) else "str"
        # Fetch the column type from the DataFrame schema.
        col_type = df.schema[column].dataType
        # Check the compatibility of value and column type.
        is_compatible = any(isinstance(col_type, t) for t in COMPATIBLE_TYPES[val_type])
        return is_compatible
    
    def raise_duplicate_cols_warnings(only_r_prefix=False):
        """
        DESCRIPTION:
            Raise warnings for duplicate columns in the resultant joined DataFrame.

        PARAMETERS:
            only_r_prefix:
                Optional Argument.
                Specifies whether in the resultant DataFrame only 'r_' prefix is added to the duplicate column names.
                Types: bool
                Default: False

        RETURNS:
            None

        EXAMPLES:
            raise_duplicate_cols_warnings()
        """

        msg = "The DataFrames have common column names. To avoid ambiguity, the duplicate column names "\
              "in the resultant DataFrame from left and right DataFrames are prefixed with 'l_' and 'r_' respectively."
        
        r_msg = "The DataFrames have common column names. To avoid ambiguity, the duplicate column names "\
                "in the resultant DataFrame from right DataFrame are prefixed 'r_'."
        
        message = r_msg if only_r_prefix else msg
        warnings.simplefilter("always", UserWarning)
        warnings.warn(message, UserWarning)
