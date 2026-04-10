<template>
  <PageContainer title="组织管理" description="维护组织树、排序和启用状态。">
    <template #filters>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="组织名称/编码" style="width: 240px;" />
        <el-button type="primary" @click="fetchList">查询</el-button>
        <el-button type="success" @click="openCreate">新增</el-button>
      </div>
    </template>

    <el-table :data="treeData" v-loading="loading" border row-key="id" default-expand-all :tree-props="{ children: 'children' }">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="组织名称" min-width="180" />
      <el-table-column prop="code" label="组织编码" min-width="140" />
      <el-table-column prop="parent_name" label="上级组织" min-width="140" />
      <el-table-column prop="sort" label="排序" width="100" />
      <el-table-column label="启用状态" width="110">
        <template #default="{ row }">
          <el-switch v-model="row.is_active" disabled />
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑组织' : '新增组织'" width="520px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="组织编码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="上级组织">
          <el-select v-model="form.parent" clearable style="width: 100%;">
            <el-option v-for="item in list" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
        <el-form-item label="启用状态">
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
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type ElForm, type FormRules } from 'element-plus'
import PageContainer from '@/components/common/PageContainer.vue'
import { createOrganization, deleteOrganization, fetchOrganizationList, updateOrganization } from '@/api/system/organization'
import { useCrud } from '@/composables/useCrud'

const keyword = ref('')
const dialogVisible = ref(false)
const formRef = ref<InstanceType<typeof ElForm>>()

const { list, loading, total, currentPage, pageSize, fetchList, handleCurrentChange, handleSizeChange } = useCrud<any>(fetchOrganizationList)
const treeData = computed(() => buildTree(filteredList.value))

const form = reactive<any>({
  id: undefined,
  name: '',
  code: '',
  parent: undefined,
  sort: 0,
  is_active: true
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入组织名称', trigger: 'blur' },
    { min: 2, max: 50, message: '组织名称长度为 2-50 位', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入组织编码', trigger: 'blur' },
    { pattern: /^[A-Za-z][A-Za-z0-9_]*$/, message: '组织编码仅支持字母、数字和下划线，且需以字母开头', trigger: 'blur' },
  ],
  sort: [
    { required: true, message: '请输入排序', trigger: 'change' },
  ],
}

const filteredList = computed(() => {
  if (!keyword.value) return list.value
  return list.value.filter((item: any) =>
    String(item.name || '').includes(keyword.value) ||
    String(item.code || '').includes(keyword.value)
  )
})

const buildTree = (items: any[]) => {
  const map = new Map<number, any>()
  const roots: any[] = []
  items.forEach((item) => map.set(item.id, { ...item, children: [] }))
  items.forEach((item) => {
    const current = map.get(item.id)
    if (item.parent && map.has(item.parent)) {
      map.get(item.parent).children.push(current)
    } else {
      roots.push(current)
    }
  })
  return roots
}

const resetForm = () => {
  form.id = undefined
  form.name = ''
  form.code = ''
  form.parent = undefined
  form.sort = 0
  form.is_active = true
}

const openCreate = () => {
  resetForm()
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

const openEdit = (row: any) => {
  form.id = row.id
  form.name = row.name
  form.code = row.code
  form.parent = row.parent
  form.sort = row.sort
  form.is_active = row.is_active
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = {
    name: form.name,
    code: form.code,
    parent: form.parent || null,
    sort: form.sort,
    is_active: form.is_active
  }
  if (form.id) {
    await updateOrganization(form.id, payload)
    ElMessage.success('编辑成功')
  } else {
    await createOrganization(payload)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchList()
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除组织【${row.name}】吗？`, '提示')
  await deleteOrganization(row.id)
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
