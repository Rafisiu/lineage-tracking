from pydantic import BaseModel, Field
from typing import Optional


class ColumnDefinition(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool = False
    default_value: Optional[str] = None
    max_length: Optional[int] = None


class TableSchema(BaseModel):
    table: str
    schema_name: Optional[str] = Field(default="public", alias="schema")
    columns: list[ColumnDefinition]
    row_count: Optional[int] = None
    estimated_size_mb: Optional[float] = None

    class Config:
        populate_by_name = True


class FieldMapping(BaseModel):
    source_field: str
    source_type: str
    destination_field: str
    destination_type: str
    transformation: Optional[str] = None
    skip: bool = False


class DatabaseConnection(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str
