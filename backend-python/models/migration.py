from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

from .schema import FieldMapping, DatabaseConnection


class MigrationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MigrationRequest(BaseModel):
    source_connection: Optional[DatabaseConnection] = None
    source_schema: str = "public"
    source_table: str
    destination_table: str
    mappings: list[FieldMapping]
    create_table: bool = True
    batch_size: int = 10000
    description: str = ""
    created_by: str = "system"


class MigrationHistory(BaseModel):
    id: str
    source: str
    destination: str
    source_table: str
    migration_time: datetime
    deskripsi: str
    tabel_fields: list[str]
    field_mappings: str
    status: MigrationStatus
    records_migrated: int
    error_message: Optional[str] = None
    duration_seconds: int
    created_by: str
    metadata: str = "{}"


class MigrationProgress(BaseModel):
    total_records: int
    processed_records: int
    percentage: float
    current_batch: Optional[int] = None
    total_batches: Optional[int] = None


class MigrationStatusResponse(BaseModel):
    id: str
    status: MigrationStatus
    progress: Optional[MigrationProgress] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
