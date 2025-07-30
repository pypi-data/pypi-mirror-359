from sqlalchemy import FromClause

from ..common import ColumnName
TableName = str
SchemaName = str
ShortTableIdentifier = tuple[SchemaName, TableName]
QualifiedTableName = str
Queryable = FromClause