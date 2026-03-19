<template>
  <el-tree-select
    v-model="selectedValue"
    :data="treeData"
    :props="treeProps"
    :multiple="multiple"
    check-strictly
    filterable
    :placeholder="placeholder"
    :clearable="clearable"
    @change="handleChange"
  />
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
    default: '选择功能'
  },
  clearable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const treeData = ref([])
const selectedValue = ref(props.modelValue)

const treeProps = {
  label: 'name',
  value: 'id',
  children: 'children'
}

const loadTree = async () => {
  try {
    const res = await axios.get('/api/v1/features/tree')
    treeData.value = res.data
  } catch (error) {
    console.error('加载功能树失败:', error)
  }
}

const handleChange = (val) => {
  emit('update:modelValue', val)
  emit('change', val)
}

watch(() => props.modelValue, (newVal) => {
  selectedValue.value = newVal
})

onMounted(() => {
  loadTree()
})
</script>

<style scoped>
.el-tree-select {
  width: 100%;
}
</style>
