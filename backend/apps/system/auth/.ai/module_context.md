# auth 模块上下文

模块职责：
- 登录、刷新 token、当前用户信息、菜单与权限下发

当前状态：
- 已有 JWT 骨架
- 已有 session-info
- 已有 my-menus / my-permissions / my-data-scopes

已知风险：
- refresh token 黑名单未实现
- 多端会话控制未实现

禁止破坏点：
- Django Admin Session 不受影响
- access / refresh 分工不能混乱
