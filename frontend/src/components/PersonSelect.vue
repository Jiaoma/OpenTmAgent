<template>
  <el-select
    v-model="selectedValue"
    filterable
    remote
    :remote-method="searchPersons"
    :loading="loading"
    :multiple="multiple"
    :placeholder="placeholder"
    :clearable="clearable"
    @change="handleChange"
  >
    <el-option
      v-for="person in persons"
      :key="person.id"
      :label="`${person.name} (${person.employee_id})`"
      :value="person.id"
    >
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 500;">{{ person.name }}</span>
        <span style="color: #999; font-size: 12px;">
          {{ person.employee_id }}
          <span v-if="person.position"> - {{ person.position }}</span>
        </span>
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
    default: '搜索人员姓名或工号'
  },
  clearable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const persons = ref([])
const loading = ref(false)
const selectedValue = ref(props.modelValue)

let searchTimer = null

const searchPersons = async (query) => {
  if (!query || query.trim() === '') {
    persons.value = []
    return
  }
  
  clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    loading.value = true
    try {
      const res = await axios.get('/api/v1/persons', {
        params: {
          search: query.trim(),
          limit: 20
        }
      })
      persons.value = res.data
    } catch (error) {
      console.error('搜索人员失败:', error)
    } finally {
      loading.value = false
    }
  }, 300)
}

const handleChange = (val) => {
  emit('update:modelValue', val)
  emit('change', val)
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
