import { defineStore } from 'pinia'
import { ref } from 'vue'
import { queryApi } from '@/api'

export interface QueryResult {
  success: boolean
  data: any[]
  rows: number
  execution_time_ms: number
  metadata: any
}

export const useQueryStore = defineStore('query', () => {
  const currentQuery = ref('')
  const queryResult = ref<QueryResult | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const executeQuery = async (query: string, format: string = 'JSON') => {
    loading.value = true
    error.value = null
    queryResult.value = null

    try {
      const response = await queryApi.execute(query, format)
      queryResult.value = response.data
      currentQuery.value = query
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearResult = () => {
    queryResult.value = null
    error.value = null
  }

  return {
    currentQuery,
    queryResult,
    loading,
    error,
    executeQuery,
    clearResult,
  }
})
