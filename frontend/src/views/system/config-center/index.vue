<template>
  <PageContainer title="配置中心" description="维护系统级参数与运行配置。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="配置键/分类" style="width: 260px;" />
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button type="success" @click="openCreate">新增</el-button>
      </div>
    </template>

    <el-table :data="filteredList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="key" label="配置键" min-width="180" />
      <el-table-column prop="category" label="分类" min-width="120" />
      <el-table-column prop="value" label="配置值" min-width="220" />
      <el-table-column prop="remark" label="备注" min-width="180" />
      <el-table-column label="敏感配置" width="100">
        <template #default="{ row }">
          {{ row.is_secret ? '是' : '否' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next"
        :total="total"
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑配置项' : '新增配置项'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="配置键">
          <el-input v-model="form.key" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="form.category" />
        </el-form-item>
        <el-form-item label="配置值">
          <el-input v-model="form.value" type="textarea" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" />
        </el-form-item>
        <el-form-item label="敏感">
          <el-switch v-model="form.is_secret" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import {
  createConfigCenterItem,
  deleteConfigCenterItem,
  fetchConfigCenterList,
  updateConfigCenterItem,
} from '@/api/system/config-center'
import { useCrud } from '@/composables/useCrud'

const keyword = ref('')
const dialogVisible = ref(false)
const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchConfigCenterList)

const filteredList = computed(() => {
  if (!keyword.value) return list.value
  return list.value.filter((item: any) =>
    [item.key, item.category].some((value) => String(value || '').includes(keyword.value))
  )
})

const form = reactive<any>({
  id: undefined,
  key: '',
  category: '',
  value: '',
  remark: '',
  is_secret: false,
  is_active: true,
})

const resetForm = () => {
  form.id = undefined
  form.key = ''
  form.category = ''
  form.value = ''
  form.remark = ''
  form.is_secret = false
  form.is_active = true
}

const openCreate = () => {
  resetForm()
  dialogVisible.value = true
}

const openEdit = (row: any) => {
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const payload = {
    key: form.key,
    category: form.category,
    value: form.value,
    remark: form.remark,
    is_secret: form.is_secret,
    is_active: form.is_active,
  }
  if (form.id) {
    await updateConfigCenterItem(form.id, payload)
    ElMessage.success('编辑成功')
  } else {
    await createConfigCenterItem(payload)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除配置项【${row.key}】吗？`, '提示')
  await deleteConfigCenterItem(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
