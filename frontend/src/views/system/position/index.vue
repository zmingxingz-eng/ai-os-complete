<template>
  <PageContainer title="岗位管理" description="维护通用岗位字典，供组织岗位分配复用。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="岗位名称/编码/类别" style="width: 260px;" />
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="success" @click="openCreate">新增</el-button>
      </div>
    </template>

    <el-table :data="filteredList" v-loading="loading" border empty-text="暂无岗位数据">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="岗位名称" min-width="160" />
      <el-table-column prop="code" label="岗位编码" min-width="150" />
      <el-table-column prop="category" label="岗位类别" min-width="140" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sort" label="排序" width="90" />
      <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑岗位' : '新增岗位'" width="520px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item label="岗位名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="岗位编码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="岗位类别">
          <el-input v-model="form.category" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
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
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type ElForm, type FormRules } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { createPosition, deletePosition, fetchPositionList, updatePosition } from '@/api/system/organization'
import { useCrud } from '@/composables/useCrud'

const keyword = ref('')
const dialogVisible = ref(false)
const formRef = ref<InstanceType<typeof ElForm>>()

const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchPositionList)

const filteredList = computed(() => {
  if (!keyword.value) return list.value
  return list.value.filter((item: any) =>
    [item.name, item.code, item.category].some((value) => String(value || '').includes(keyword.value))
  )
})

const form = reactive<any>({
  id: undefined,
  name: '',
  code: '',
  category: '',
  status: 'active',
  sort: 0,
  remark: '',
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入岗位名称', trigger: 'blur' },
    { min: 2, max: 50, message: '岗位名称长度为 2-50 位', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入岗位编码', trigger: 'blur' },
    { pattern: /^[A-Za-z][A-Za-z0-9_]*$/, message: '岗位编码仅支持字母、数字和下划线，且需以字母开头', trigger: 'blur' },
  ],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  sort: [{ required: true, message: '请输入排序', trigger: 'change' }],
}

const resetForm = () => {
  form.id = undefined
  form.name = ''
  form.code = ''
  form.category = ''
  form.status = 'active'
  form.sort = 0
  form.remark = ''
}

const handleReset = () => {
  keyword.value = ''
  fetchList()
}

const openCreate = async () => {
  resetForm()
  dialogVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const openEdit = async (row: any) => {
  form.id = row.id
  form.name = row.name
  form.code = row.code
  form.category = row.category || ''
  form.status = row.status
  form.sort = row.sort
  form.remark = row.remark || ''
  dialogVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    name: form.name,
    code: form.code,
    category: form.category,
    status: form.status,
    is_active: form.status === 'active',
    sort: form.sort,
    remark: form.remark,
  }
  if (form.id) {
    await updatePosition(form.id, payload)
    ElMessage.success('编辑成功')
  } else {
    await createPosition(payload)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除岗位【${row.name}】吗？`, '提示')
  await deletePosition(row.id)
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
