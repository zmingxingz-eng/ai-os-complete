# AI OS 2.0 Django Admin Enterprise v2.0.0

一人团队 AI 开发操作系统模板（重建骨架版）。

## 技术栈
- Backend: Django + Django REST Framework + Django Admin
- Frontend: Vue3 + TypeScript + Element Plus + Pinia + Vite
- AI OS: Rules + Skills + Workflows + Prompts + Memory + Context Runtime

## 版本重点
- Django 原生 `Group / Permission` 作为角色权限主模型
- 自定义 `Menu / GroupMenu / GroupDataScope` 作为导航与数据权限扩展
- Vue3 + Element Plus 系统管理前台骨架
- JWT 认证骨架
- 适合作为后续业务域继续扩展的系统管理域母版

## 启动建议
1. 先进入 `backend/` 安装依赖并执行迁移
2. 再进入 `frontend/` 安装依赖启动前端
3. 根据项目需要继续补齐真实业务模块

## 目录说明
- `backend/`：Django + DRF 后端工程，承载系统管理域与后续业务域接口
- `frontend/`：Vue3 + Element Plus 前端工程，承载系统管理前台
- `.ai/`：AI 协作运行时上下文、规则注入、记忆与任务续做资产
- `.platform/`：平台方法层资产，包含战略、产品、架构、代码工厂、质量体系、DevOps、知识库、AI 编排与指标系统
