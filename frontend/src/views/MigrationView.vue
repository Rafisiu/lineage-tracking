<template>
  <div class="migration-view">
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step title="Source Configuration" />
      <el-step title="Schema Analysis" />
      <el-step title="Mapping Configuration" />
      <el-step title="Execution" />
    </el-steps>

    <div class="step-content">
      <!-- Step 1: Source Configuration -->
      <el-card v-show="currentStep === 0" class="step-card">
        <template #header>
          <span>Configure PostgreSQL Source</span>
        </template>

        <el-form :model="sourceConfig" label-width="140px">
          <el-form-item label="Schema">
            <el-input v-model="sourceConfig.schema" placeholder="public" />
          </el-form-item>
          <el-form-item label="Table Name">
            <el-input v-model="sourceConfig.table" placeholder="users" />
          </el-form-item>

          <el-divider content-position="left">Connection (Optional - uses default if empty)</el-divider>

          <el-form-item label="Host">
            <el-input v-model="sourceConfig.connection.host" placeholder="Leave empty for default" />
          </el-form-item>
          <el-form-item label="Port">
            <el-input-number v-model="sourceConfig.connection.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="Database">
            <el-input v-model="sourceConfig.connection.database" placeholder="Leave empty for default" />
          </el-form-item>
          <el-form-item label="User">
            <el-input v-model="sourceConfig.connection.user" placeholder="Leave empty for default" />
          </el-form-item>
          <el-form-item label="Password">
            <el-input v-model="sourceConfig.connection.password" type="password" show-password placeholder="Leave empty for default" />
          </el-form-item>
        </el-form>

        <div class="step-actions">
          <el-button type="primary" @click="handleAnalyzeSource" :loading="migrationStore.loading">
            Next: Analyze Schema
          </el-button>
        </div>
      </el-card>

      <!-- Step 2: Schema Analysis -->
      <el-card v-show="currentStep === 1" class="step-card">
        <template #header>
          <div class="card-header">
            <span>Source Table Schema</span>
            <div v-if="migrationStore.sourceSchema">
              <el-tag>{{ migrationStore.sourceSchema.row_count?.toLocaleString() }} rows</el-tag>
              <el-tag type="info" style="margin-left: 10px">
                {{ migrationStore.sourceSchema.estimated_size_mb?.toFixed(2) }} MB
              </el-tag>
            </div>
          </div>
        </template>

        <el-table
          v-if="migrationStore.sourceSchema"
          :data="migrationStore.sourceSchema.columns"
          stripe
          border
        >
          <el-table-column prop="name" label="Column Name" width="200" />
          <el-table-column prop="type" label="PostgreSQL Type" width="180" />
          <el-table-column label="Nullable" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.nullable ? 'info' : 'warning'" size="small">
                {{ scope.row.nullable ? 'Yes' : 'No' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Primary Key" width="120">
            <template #default="scope">
              <el-icon v-if="scope.row.primary_key" color="#67C23A"><Check /></el-icon>
            </template>
          </el-table-column>
        </el-table>

        <div class="step-actions">
          <el-button @click="currentStep = 0">Back</el-button>
          <el-button type="primary" @click="handleGenerateMapping" :loading="migrationStore.loading">
            Next: Generate Mapping
          </el-button>
        </div>
      </el-card>

      <!-- Step 3: Mapping Configuration -->
      <el-card v-show="currentStep === 2" class="step-card">
        <template #header>
          <span>Field Mapping Configuration</span>
        </template>

        <el-form :model="migrationConfig" label-width="160px" style="margin-bottom: 20px">
          <el-form-item label="Destination Table">
            <el-input v-model="migrationConfig.destination_table" placeholder="users_clickhouse" />
          </el-form-item>
          <el-form-item label="Description">
            <el-input v-model="migrationConfig.description" type="textarea" :rows="2" placeholder="Migration description" />
          </el-form-item>
          <el-form-item label="Batch Size">
            <el-input-number v-model="migrationConfig.batch_size" :min="100" :max="100000" :step="1000" />
          </el-form-item>
          <el-form-item label="Create Table">
            <el-switch v-model="migrationConfig.create_table" />
          </el-form-item>
        </el-form>

        <el-alert
          v-if="migrationStore.warnings.length > 0"
          type="warning"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #title>
            <div>Mapping Warnings:</div>
            <ul style="margin: 5px 0; padding-left: 20px">
              <li v-for="(warning, index) in migrationStore.warnings" :key="index">{{ warning }}</li>
            </ul>
          </template>
        </el-alert>

        <el-table :data="migrationStore.mappings" stripe border>
          <el-table-column prop="source_field" label="Source Field" width="180" />
          <el-table-column prop="source_type" label="Source Type" width="150" />
          <el-table-column label="Destination Field" width="180">
            <template #default="scope">
              <el-input v-model="scope.row.destination_field" size="small" :disabled="scope.row.skip" />
            </template>
          </el-table-column>
          <el-table-column label="Destination Type" width="180">
            <template #default="scope">
              <el-input v-model="scope.row.destination_type" size="small" :disabled="scope.row.skip" />
            </template>
          </el-table-column>
          <el-table-column label="Skip" width="80" align="center">
            <template #default="scope">
              <el-checkbox v-model="scope.row.skip" />
            </template>
          </el-table-column>
        </el-table>

        <el-divider content-position="left">Generated DDL</el-divider>
        <el-input
          v-model="migrationStore.suggestedDDL"
          type="textarea"
          :rows="8"
          readonly
          class="ddl-preview"
        />

        <div class="step-actions">
          <el-button @click="currentStep = 1">Back</el-button>
          <el-button type="primary" @click="handleExecuteMigration" :loading="migrationStore.loading">
            Start Migration
          </el-button>
        </div>
      </el-card>

      <!-- Step 4: Execution -->
      <el-card v-show="currentStep === 3" class="step-card">
        <template #header>
          <span>Migration Progress</span>
        </template>

        <div v-if="migrationStore.migrationStatus" class="migration-status">
          <el-result
            v-if="migrationStore.migrationStatus.status === 'completed'"
            icon="success"
            title="Migration Completed Successfully"
          >
            <template #sub-title>
              <p>Migration ID: {{ migrationStore.currentMigrationId }}</p>
              <div class="status-stats">
                <el-statistic title="Records Migrated" :value="migrationStore.migrationStatus.progress?.processed_records || 0" />
              </div>
            </template>
            <template #extra>
              <el-button type="primary" @click="handleReset">Start New Migration</el-button>
              <el-button @click="$router.push('/history')">View History</el-button>
            </template>
          </el-result>

          <el-result
            v-else-if="migrationStore.migrationStatus.status === 'failed'"
            icon="error"
            title="Migration Failed"
          >
            <template #sub-title>
              <p>{{ migrationStore.migrationStatus.error_message }}</p>
            </template>
            <template #extra>
              <el-button type="primary" @click="currentStep = 2">Back to Configuration</el-button>
              <el-button @click="handleReset">Start New Migration</el-button>
            </template>
          </el-result>

          <div v-else class="progress-container">
            <el-progress
              :percentage="migrationStore.migrationStatus.progress?.percentage || 0"
              :status="migrationStore.migrationStatus.status === 'running' ? undefined : 'success'"
            />
            <div class="progress-stats">
              <p>Status: <el-tag>{{ migrationStore.migrationStatus.status }}</el-tag></p>
              <p>Processed: {{ migrationStore.migrationStatus.progress?.processed_records?.toLocaleString() || 0 }} / {{ migrationStore.migrationStatus.progress?.total_records?.toLocaleString() || 0 }}</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import { useMigrationStore } from '@/stores/migration'

const migrationStore = useMigrationStore()
const currentStep = ref(0)

const sourceConfig = reactive({
  schema: 'public',
  table: '',
  connection: {
    host: '',
    port: 5432,
    database: '',
    user: '',
    password: '',
  },
})

const migrationConfig = reactive({
  destination_table: '',
  description: '',
  batch_size: 10000,
  create_table: true,
})

const hasConnection = () => {
  return sourceConfig.connection.host && sourceConfig.connection.database && sourceConfig.connection.user
}

const handleAnalyzeSource = async () => {
  if (!sourceConfig.table) {
    ElMessage.warning('Please enter a table name')
    return
  }

  try {
    const payload: any = {
      schema: sourceConfig.schema,
      table: sourceConfig.table,
    }

    if (hasConnection()) {
      payload.connection = sourceConfig.connection
    }

    await migrationStore.analyzeSource(payload)
    currentStep.value = 1
    ElMessage.success('Schema analyzed successfully')
  } catch (error) {
    ElMessage.error('Failed to analyze source schema')
  }
}

const handleGenerateMapping = async () => {
  if (!migrationConfig.destination_table) {
    migrationConfig.destination_table = `${sourceConfig.table}_clickhouse`
  }

  try {
    await migrationStore.suggestMapping(migrationConfig.destination_table)
    currentStep.value = 2
    ElMessage.success('Mapping generated successfully')
  } catch (error) {
    ElMessage.error('Failed to generate mapping')
  }
}

const handleExecuteMigration = async () => {
  try {
    const payload: any = {
      source_schema: sourceConfig.schema,
      source_table: sourceConfig.table,
      destination_table: migrationConfig.destination_table,
      mappings: migrationStore.mappings,
      create_table: migrationConfig.create_table,
      batch_size: migrationConfig.batch_size,
      description: migrationConfig.description,
    }

    if (hasConnection()) {
      payload.source_connection = sourceConfig.connection
    }

    await migrationStore.executeMigration(payload)
    currentStep.value = 3

    // Poll for status
    pollMigrationStatus()
    ElMessage.success('Migration started')
  } catch (error) {
    ElMessage.error('Failed to start migration')
  }
}

let pollingInterval: any = null

const pollMigrationStatus = () => {
  if (!migrationStore.currentMigrationId) return

  pollingInterval = setInterval(async () => {
    try {
      await migrationStore.getMigrationStatus(migrationStore.currentMigrationId!)

      if (migrationStore.migrationStatus?.status === 'completed' ||
          migrationStore.migrationStatus?.status === 'failed') {
        clearInterval(pollingInterval)
      }
    } catch (error) {
      console.error('Failed to get migration status:', error)
    }
  }, 2000)
}

const handleReset = () => {
  migrationStore.reset()
  currentStep.value = 0
  sourceConfig.table = ''
  migrationConfig.destination_table = ''
  migrationConfig.description = ''
  if (pollingInterval) {
    clearInterval(pollingInterval)
  }
}
</script>

<style scoped>
.migration-view {
  max-width: 1400px;
  margin: 0 auto;
}

.step-content {
  margin-top: 30px;
}

.step-card {
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.ddl-preview :deep(textarea) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.migration-status {
  padding: 20px 0;
}

.progress-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 40px 0;
}

.progress-stats {
  margin-top: 20px;
  text-align: center;
}

.progress-stats p {
  margin: 10px 0;
  font-size: 14px;
}

.status-stats {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 40px;
}
</style>
