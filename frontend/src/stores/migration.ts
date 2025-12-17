import { defineStore } from 'pinia'
import { ref } from 'vue'
import { migrationApi } from '@/api'

export interface TableSchema {
  table: string
  schema?: string
  columns: ColumnDefinition[]
  row_count?: number
  estimated_size_mb?: number
}

export interface ColumnDefinition {
  name: string
  type: string
  nullable: boolean
  primary_key?: boolean
  default_value?: string
  max_length?: number
}

export interface FieldMapping {
  source_field: string
  source_type: string
  destination_field: string
  destination_type: string
  transformation?: string | null
  skip?: boolean
}

export interface MigrationProgress {
  total_records: number
  processed_records: number
  percentage: number
}

export const useMigrationStore = defineStore('migration', () => {
  const sourceSchema = ref<TableSchema | null>(null)
  const mappings = ref<FieldMapping[]>([])
  const suggestedDDL = ref('')
  const warnings = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const currentMigrationId = ref<string | null>(null)
  const migrationStatus = ref<any>(null)

  const analyzeSource = async (data: any) => {
    loading.value = true
    error.value = null

    try {
      const response = await migrationApi.analyzeSource(data)
      sourceSchema.value = response.data.data
      return response.data.data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const suggestMapping = async (destinationTable: string) => {
    if (!sourceSchema.value) {
      throw new Error('Source schema not available')
    }

    loading.value = true
    error.value = null

    try {
      const response = await migrationApi.suggestMapping({
        source_schema: sourceSchema.value,
        destination_table: destinationTable,
      })

      const data = response.data.data
      mappings.value = data.mappings
      suggestedDDL.value = data.suggested_ddl
      warnings.value = data.warnings

      return data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const executeMigration = async (migrationData: any) => {
    loading.value = true
    error.value = null

    try {
      const response = await migrationApi.execute(migrationData)
      currentMigrationId.value = response.data.migration_id
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getMigrationStatus = async (migrationId: string) => {
    try {
      const response = await migrationApi.getStatus(migrationId)
      migrationStatus.value = response.data.data
      return response.data.data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    }
  }

  const reset = () => {
    sourceSchema.value = null
    mappings.value = []
    suggestedDDL.value = ''
    warnings.value = []
    error.value = null
    currentMigrationId.value = null
    migrationStatus.value = null
  }

  return {
    sourceSchema,
    mappings,
    suggestedDDL,
    warnings,
    loading,
    error,
    currentMigrationId,
    migrationStatus,
    analyzeSource,
    suggestMapping,
    executeMigration,
    getMigrationStatus,
    reset,
  }
})
