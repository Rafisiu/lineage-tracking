<template>
  <div class="s3-explorer-view">
    <el-row :gutter="20">
      <!-- File Browser Panel -->
      <el-col :span="8">
        <el-card class="browser-card">
          <template #header>
            <div class="card-header">
              <span>S3 File Browser</span>
              <el-button size="small" @click="refreshBuckets" :loading="loadingBuckets">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>

          <!-- Bucket Selection -->
          <el-select
            v-model="selectedBucket"
            placeholder="Select bucket"
            @change="onBucketChange"
            style="width: 100%; margin-bottom: 10px;"
          >
            <el-option
              v-for="bucket in buckets"
              :key="bucket.name"
              :label="bucket.name"
              :value="bucket.name"
            />
          </el-select>

          <!-- Current Path -->
          <div class="path-bar" v-if="selectedBucket">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item @click="navigateTo('')">
                {{ selectedBucket }}
              </el-breadcrumb-item>
              <el-breadcrumb-item
                v-for="(part, index) in pathParts"
                :key="index"
                @click="navigateTo(pathParts.slice(0, index + 1).join('/') + '/')"
              >
                {{ part }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <!-- File List -->
          <el-table
            :data="files"
            v-loading="loadingFiles"
            @row-click="onFileClick"
            highlight-current-row
            size="small"
            max-height="400"
          >
            <el-table-column prop="name" label="Name">
              <template #default="{ row }">
                <el-icon v-if="row.is_dir"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
                {{ getFileName(row.name) }}
              </template>
            </el-table-column>
            <el-table-column prop="size" label="Size" width="80">
              <template #default="{ row }">
                {{ row.is_dir ? '-' : formatSize(row.size) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- Query Panel -->
      <el-col :span="16">
        <el-card class="query-card">
          <template #header>
            <div class="card-header">
              <span>Query S3 Data</span>
              <el-tag v-if="selectedFile" type="info" size="small">
                {{ selectedFile }}
              </el-tag>
            </div>
          </template>

          <!-- Query Input -->
          <el-input
            v-model="sqlQuery"
            type="textarea"
            :rows="4"
            placeholder="Enter SQL query (e.g., SELECT * FROM data WHERE column > 100)"
          />

          <div class="query-actions">
            <el-button
              type="primary"
              @click="executeQuery"
              :loading="loadingQuery"
              :disabled="!selectedFile"
            >
              <el-icon><VideoPlay /></el-icon>
              Execute Query (100 rows)
            </el-button>
            <el-button @click="getSchema" :disabled="!selectedFile">
              <el-icon><List /></el-icon>
              Schema
            </el-button>
          </div>

          <!-- Error Alert -->
          <el-alert
            v-if="error"
            :title="error"
            type="error"
            show-icon
            closable
            @close="error = ''"
            style="margin-top: 10px;"
          />

          <!-- Results -->
          <div class="results-section" v-if="queryResult">
            <div class="results-info">
              <el-tag type="success">{{ queryResult.row_count }} rows</el-tag>
              <el-tag type="info" v-if="queryResult.execution_time_ms">
                {{ queryResult.execution_time_ms }}ms
              </el-tag>
            </div>

            <el-table
              :data="queryResult.data"
              border
              stripe
              size="small"
              max-height="400"
              style="margin-top: 10px;"
            >
              <el-table-column
                v-for="col in queryResult.columns"
                :key="col"
                :prop="col"
                :label="col"
                min-width="120"
              >
                <template #default="{ row }">
                  {{ formatValue(row[col]) }}
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Schema Display -->
          <div class="schema-section" v-if="fileSchema && !queryResult">
            <h4>File Schema</h4>
            <el-table :data="fileSchema" size="small" border>
              <el-table-column prop="column_name" label="Column" />
              <el-table-column prop="column_type" label="Type" />
              <el-table-column prop="null" label="Nullable" width="80" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { s3Api } from '../api'
import { Refresh, Folder, Document, VideoPlay, List } from '@element-plus/icons-vue'

// State
const buckets = ref<any[]>([])
const selectedBucket = ref('')
const currentPath = ref('')
const files = ref<any[]>([])
const selectedFile = ref('')

const sqlQuery = ref('')
const queryResult = ref<any>(null)
const fileSchema = ref<any>(null)

const loadingBuckets = ref(false)
const loadingFiles = ref(false)
const loadingQuery = ref(false)
const error = ref('')

// Computed
const pathParts = computed(() => {
  if (!currentPath.value) return []
  return currentPath.value.split('/').filter(p => p)
})

// Methods
const refreshBuckets = async () => {
  loadingBuckets.value = true
  try {
    const response = await s3Api.listBuckets()
    buckets.value = response.data.data || []
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message
  } finally {
    loadingBuckets.value = false
  }
}

const onBucketChange = () => {
  currentPath.value = ''
  selectedFile.value = ''
  queryResult.value = null
  fileSchema.value = null
  loadFiles()
}

const loadFiles = async () => {
  if (!selectedBucket.value) return

  loadingFiles.value = true
  try {
    const response = await s3Api.browse(selectedBucket.value, currentPath.value)
    files.value = response.data.data || []
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message
    files.value = []
  } finally {
    loadingFiles.value = false
  }
}

const navigateTo = (path: string) => {
  currentPath.value = path
  selectedFile.value = ''
  queryResult.value = null
  fileSchema.value = null
  loadFiles()
}

const onFileClick = (row: any) => {
  if (row.is_dir) {
    currentPath.value = row.name
    loadFiles()
  } else {
    selectedFile.value = row.name
    queryResult.value = null
    fileSchema.value = null
    // Auto-generate query for the selected file
    sqlQuery.value = 'SELECT * FROM data'
  }
}

const getFileName = (path: string) => {
  const parts = path.split('/')
  return parts[parts.length - 1] || parts[parts.length - 2] + '/'
}

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatValue = (value: any) => {
  if (value === null || value === undefined) return 'NULL'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const executeQuery = async () => {
  if (!selectedFile.value) return

  loadingQuery.value = true
  error.value = ''
  fileSchema.value = null

  try {
    const response = await s3Api.query(
      selectedBucket.value,
      selectedFile.value,
      sqlQuery.value || undefined,
      100
    )
    queryResult.value = response.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message
    queryResult.value = null
  } finally {
    loadingQuery.value = false
  }
}

const getSchema = async () => {
  if (!selectedFile.value) return

  error.value = ''
  queryResult.value = null

  try {
    const response = await s3Api.getSchema(selectedBucket.value, selectedFile.value)
    fileSchema.value = response.data.data || []
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message
  }
}

// Lifecycle
onMounted(() => {
  refreshBuckets()
})
</script>

<style scoped>
.s3-explorer-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.browser-card {
  height: 100%;
}

.path-bar {
  margin-bottom: 10px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.path-bar .el-breadcrumb__item {
  cursor: pointer;
}

.query-card {
  height: 100%;
}

.query-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.limit-label {
  font-size: 12px;
  color: #909399;
}

.results-section {
  margin-top: 15px;
}

.results-info {
  display: flex;
  gap: 10px;
}

.schema-section {
  margin-top: 15px;
}

.schema-section h4 {
  margin: 0 0 10px 0;
  color: #606266;
}
</style>
