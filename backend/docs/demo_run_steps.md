# 演示运行步骤

## 1. 进入 backend
```bash
cd backend
python -m venv .venv
```

## 2. 安装依赖
```bash
pip install -r requirements/dev.txt
```

## 3. 初始化演示数据
```bash
python scripts/init_demo_all.py
```

## 4. 启动后端
```bash
python manage.py runserver
```

## 5. 启动前端
```bash
cd ../frontend
npm install
npm run dev
```

## 默认账号
- admin / Admin123456
