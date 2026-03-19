<template>
  <el-select
    v-model="selectedValue"
    filterable
    remote
    :remote-method="searchTasks"
    :loading="loading"
    :multiple="multiple"
    :placeholder="placeholder"
    :clearable="clearable"
    @change="handleChange"
  >
    <el-option
      v-for="task in tasks"
      :key="task.id"
      :label="task.name"
      :value="task.id"
    >
      <div>
        <div style="font-weight: 500;">{{ task.name }}</div>
        <div style="color: #999; font-size: 12px;">
          {{ task.start_date }} ~ {{ task.end_date }}
          <span :style="{ color: getStatusColor(task.status), marginLeft: '8px' }">
            {{ getStatusText(task.status) }}
          </span>
        </div>
      </div>
    </el-option>
  </el-select>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: [String, Array],
    default: ''
  },
  multiple: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '搜索任务名称'
  },
  clearable: {
    type: Boolean,
    default: true
  },
  iterationId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const tasks = ref([])
const loading = ref(false)
const selectedValue = ref(props.modelValue)

let searchTimer = null

const searchTasks = async (query) => {
  if (!query || query.trim() === '') {
    tasks.value = []
    return
  }
  
  clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    loading.value = true
    try {
      const params = {
        search: query.trim(),
        limit: 20
      }
      if (props.iterationId) {
        params.iteration_id = props.iterationId
      }
      
      const res = await axios.get('/api/v1/tasks', { params })
      tasks.value = res.data
    } catch (error) {
      console.error('搜索任务失败:', error)
    } finally {
      loading.value = false
    }
  }, 300)
}

const handleChange = (val) => {
  emit('update:modelValue', val)
  emit('change', val)
}

const getStatusColor = (status) => {
  const colors = {
    pending: '#909399',
    in_progress: '#409EFF',
    completed: '#67C23A'
  }
  return colors[status] || '#909399'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成'
  }
  return texts[status] || status
}

watch(() => props.modelValue, (newVal) => {
  selectedValue.value = newVal
})

onMounted(() => {
  if (props.modelValue) {
    if (props.multiple && Array.isArray(props.modelValue)) {
      selectedValue.value = props.modelValue
    } else if (!props.multiple && typeof props.modelValue === 'string') {
      selectedValue.value = props.modelValue
    }
  }
})
</script>

<style scoped>
.el-select {
  width: 100%;
}
</style>
