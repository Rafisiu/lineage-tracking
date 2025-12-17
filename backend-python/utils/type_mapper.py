import re
from typing import Optional

# PostgreSQL to ClickHouse type mapping
TYPE_MAPPING = {
    # Integer types
    "smallint": "Int16",
    "int2": "Int16",
    "integer": "Int32",
    "int": "Int32",
    "int4": "Int32",
    "serial": "Int32",
    "bigint": "Int64",
    "int8": "Int64",
    "bigserial": "Int64",

    # Floating point types
    "real": "Float32",
    "float4": "Float32",
    "double precision": "Float64",
    "float8": "Float64",
    "numeric": "Decimal128(38)",
    "decimal": "Decimal128(38)",

    # String types
    "varchar": "String",
    "character varying": "String",
    "text": "String",
    "char": "String",
    "character": "String",
    "bpchar": "String",

    # Date/Time types
    "date": "Date",
    "timestamp": "DateTime",
    "timestamp without time zone": "DateTime",
    "timestamptz": "DateTime64(3)",
    "timestamp with time zone": "DateTime64(3)",
    "time": "String",
    "time without time zone": "String",
    "timetz": "String",
    "time with time zone": "String",

    # Boolean
    "boolean": "UInt8",
    "bool": "UInt8",

    # JSON types
    "json": "String",
    "jsonb": "String",

    # UUID
    "uuid": "UUID",

    # Binary
    "bytea": "String",
}


def map_postgres_to_clickhouse(postgres_type: str, nullable: bool = True) -> str:
    """Map PostgreSQL type to ClickHouse type."""
    # Normalize type name
    pg_type = postgres_type.lower().strip()

    # Handle arrays
    if pg_type.endswith("[]"):
        base_type = pg_type[:-2]
        ch_base_type = TYPE_MAPPING.get(base_type, "String")
        ch_type = f"Array({ch_base_type})"
        return ch_type

    # Handle numeric with precision
    decimal_match = re.match(r"(?:numeric|decimal)\((\d+),\s*(\d+)\)", pg_type)
    if decimal_match:
        precision, scale = decimal_match.groups()
        ch_type = f"Decimal({precision},{scale})"
        if nullable:
            return f"Nullable({ch_type})"
        return ch_type

    # Handle varchar with length (ignore length)
    varchar_match = re.match(r"(?:varchar|character varying|char|character)\((\d+)\)", pg_type)
    if varchar_match:
        ch_type = "String"
        if nullable:
            return f"Nullable({ch_type})"
        return ch_type

    # Standard mapping
    ch_type = TYPE_MAPPING.get(pg_type, "String")

    if nullable:
        return f"Nullable({ch_type})"
    return ch_type


def validate_type_mapping(postgres_type: str) -> dict:
    """Validate if PostgreSQL type can be mapped to ClickHouse."""
    pg_type = postgres_type.lower().strip()

    # Handle arrays
    if pg_type.endswith("[]"):
        base_type = pg_type[:-2]
        if base_type in TYPE_MAPPING:
            return {
                "valid": True,
                "warning": "Array types may require special handling",
                "clickhouse_type": f"Array({TYPE_MAPPING[base_type]})"
            }
        return {
            "valid": True,
            "warning": f"Unknown array base type '{base_type}', using String",
            "clickhouse_type": "Array(String)"
        }

    # Handle numeric with precision
    if re.match(r"(?:numeric|decimal)\((\d+),\s*(\d+)\)", pg_type):
        return {"valid": True, "clickhouse_type": "Decimal(p,s)"}

    # Handle varchar with length
    if re.match(r"(?:varchar|character varying|char|character)\((\d+)\)", pg_type):
        return {"valid": True, "clickhouse_type": "String"}

    # Standard types
    if pg_type in TYPE_MAPPING:
        return {"valid": True, "clickhouse_type": TYPE_MAPPING[pg_type]}

    return {
        "valid": True,
        "warning": f"Unknown type '{postgres_type}', defaulting to String",
        "clickhouse_type": "String"
    }
