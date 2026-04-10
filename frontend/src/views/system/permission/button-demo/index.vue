<template>
  <div>
    <el-button v-permission="'notice.manage'" type="primary">允许：公告管理</el-button>
    <el-button v-permission="'user.export'" type="success">允许：用户导出</el-button>
  </div>
</template>
