<template>
  <div class="history-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Migration History</span>
          <el-button type="primary" @click="loadHistory" :loading="loading">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>

      <div class="filters">
        <el-select v-model="statusFilter" placeholder="Filter by status" clearable @change="loadHistory">
          <el-option label="All" value="" />
          <el-option label="Completed" value="completed" />
          <el-option label="Running" value="running" />
          <el-option label="Failed" value="failed" />
        </el-select>
      </div>

      <el-table
        :data="historyData"
        stripe
        border
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="Migration ID" width="280" show-overflow-tooltip />

        <el-table-column label="Status" width="120">
          <template #default="scope">
            <el-tag
              :type="getStatusType(scope.row.status)"
              effect="dark"
            >
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="source_table" label="Source Table" width="150" />
        <el-table-column prop="destination" label="Destination Table" width="180" />

        <el-table-column label="Records" width="120" align="right">
          <template #default="scope">
            {{ scope.row.records_migrated?.toLocaleString() || 0 }}
          </template>
        </el-table-column>

        <el-table-column label="Duration" width="100">
          <template #default="scope">
            {{ formatDuration(scope.row.duration_seconds) }}
          </template>
        </el-table-column>

        <el-table-column prop="migration_time" label="Migration Time" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.migration_time) }}
          </template>
        </el-table-column>

        <el-table-column prop="deskripsi" label="Description" min-width="200" show-overflow-tooltip />

        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="showDetails(scope.row)"
              link
            >
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="loadHistory"
          @current-change="loadHistory"
        />
      </div>
    </el-card>

    <!-- Details Dialog -->
    <el-dialog
      v-model="detailsVisible"
      title="Migration Details"
      width="800px"
    >
      <div v-if="selectedMigration" class="migration-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Migration ID">
            {{ selectedMigration.id }}
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusType(selectedMigration.status)">
              {{ selectedMigration.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Source">
            {{ selectedMigration.source }}
          </el-descriptions-item>
          <el-descriptions-item label="Source Table">
            {{ selectedMigration.source_table }}
          </el-descriptions-item>
          <el-descriptions-item label="Destination Table">
            {{ selectedMigration.destination }}
          </el-descriptions-item>
          <el-descriptions-item label="Records Migrated">
            {{ selectedMigration.records_migrated?.toLocaleString() || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="Duration">
            {{ formatDuration(selectedMigration.duration_seconds) }}
          </el-descriptions-item>
          <el-descriptions-item label="Migration Time">
            {{ formatDate(selectedMigration.migration_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="Created By">
            {{ selectedMigration.created_by }}
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            {{ selectedMigration.deskripsi || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedMigration.error_message" label="Error Message" :span="2">
            <el-alert type="error" :closable="false" :title="selectedMigration.error_message" />
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">Migrated Fields</el-divider>
        <el-tag
          v-for="field in selectedMigration.tabel_fields"
          :key="field"
          style="margin: 5px"
        >
          {{ field }}
        </el-tag>

        <el-divider content-position="left">Field Mappings</el-divider>
        <el-table
          :data="parseMappings(selectedMigration.field_mappings)"
          stripe
          border
          max-height="300"
        >
          <el-table-column prop="source_field" label="Source Field" width="150" />
          <el-table-column prop="source_type" label="Source Type" width="130" />
          <el-table-column prop="destination_field" label="Destination Field" width="150" />
          <el-table-column prop="destination_type" label="Destination Type" width="150" />
          <el-table-column label="Skipped" width="80" align="center">
            <template #default="scope">
              <el-icon v-if="scope.row.skip" color="#F56C6C"><Close /></el-icon>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Close } from '@element-plus/icons-vue'
import { migrationApi } from '@/api'

const loading = ref(false)
const historyData = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')

const detailsVisible = ref(false)
const selectedMigration = ref<any>(null)

const loadHistory = async () => {
  loading.value = true
  try {
    const offset = (currentPage.value - 1) * pageSize.value
    const response = await migrationApi.getHistory({
      limit: pageSize.value,
      offset,
      status: statusFilter.value || undefined,
    })

    historyData.value = response.data.data.migrations
    total.value = response.data.data.total
  } catch (error: any) {
    ElMessage.error('Failed to load migration history')
  } finally {
    loading.value = false
  }
}

const showDetails = (migration: any) => {
  selectedMigration.value = migration
  detailsVisible.value = true
}

const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    completed: 'success',
    running: 'primary',
    failed: 'danger',
    pending: 'info',
  }
  return types[status] || 'info'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString()
}

const formatDuration = (seconds: number) => {
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}m ${remainingSeconds}s`
}

const parseMappings = (mappingsJson: string) => {
  try {
    return JSON.parse(mappingsJson)
  } catch {
    return []
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-view {
  max-width: 1600px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.migration-details {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
