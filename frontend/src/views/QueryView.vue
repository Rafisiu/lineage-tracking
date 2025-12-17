<template>
  <div class="query-view">
    <el-card class="query-card">
      <template #header>
        <div class="card-header">
          <span>SQL Query Editor</span>
        </div>
      </template>

      <div class="query-editor">
        <el-input
          v-model="query"
          type="textarea"
          :rows="10"
          placeholder="Enter your ClickHouse SQL query here...
Example:
SELECT * FROM system.tables LIMIT 10"
          class="query-input"
        />
      </div>

      <div class="query-actions">
        <el-button
          type="primary"
          :loading="queryStore.loading"
          @click="handleExecuteQuery"
          :disabled="!query.trim()"
        >
          <el-icon><CaretRight /></el-icon>
          Execute Query
        </el-button>
        <el-button @click="handleClearQuery">
          <el-icon><Delete /></el-icon>
          Clear
        </el-button>
      </div>
    </el-card>

    <el-card v-if="queryStore.error" class="result-card error-card">
      <el-alert
        :title="queryStore.error"
        type="error"
        :closable="false"
        show-icon
      />
    </el-card>

    <el-card v-if="queryStore.queryResult" class="result-card">
      <template #header>
        <div class="card-header">
          <span>Query Results</span>
          <div class="result-meta">
            <el-tag type="success">{{ queryStore.queryResult.rows }} rows</el-tag>
            <el-tag type="info">{{ queryStore.queryResult.execution_time_ms }}ms</el-tag>
          </div>
        </div>
      </template>

      <div class="result-content">
        <el-table
          :data="queryStore.queryResult.data"
          stripe
          border
          style="width: 100%"
          max-height="500"
          v-if="queryStore.queryResult.data && queryStore.queryResult.data.length > 0"
        >
          <el-table-column
            v-for="column in getColumns(queryStore.queryResult.data)"
            :key="column"
            :prop="column"
            :label="column"
            min-width="150"
          >
            <template #default="scope">
              <span>{{ formatValue(scope.row[column]) }}</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-else
          description="No data returned"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { CaretRight, Delete } from '@element-plus/icons-vue'
import { useQueryStore } from '@/stores/query'

const queryStore = useQueryStore()
const query = ref('')

const handleExecuteQuery = async () => {
  try {
    await queryStore.executeQuery(query.value)
    ElMessage.success('Query executed successfully')
  } catch (error) {
    ElMessage.error('Failed to execute query')
  }
}

const handleClearQuery = () => {
  query.value = ''
  queryStore.clearResult()
}

const getColumns = (data: any[]): string[] => {
  if (!data || data.length === 0) return []
  return Object.keys(data[0])
}

const formatValue = (value: any): string => {
  if (value === null || value === undefined) return 'NULL'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
</script>

<style scoped>
.query-view {
  max-width: 1400px;
  margin: 0 auto;
}

.query-card,
.result-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.result-meta {
  display: flex;
  gap: 10px;
}

.query-editor {
  margin-bottom: 20px;
}

.query-input :deep(textarea) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
}

.query-actions {
  display: flex;
  gap: 10px;
}

.result-content {
  overflow-x: auto;
}

.error-card {
  border-color: #f56c6c;
}
</style>
