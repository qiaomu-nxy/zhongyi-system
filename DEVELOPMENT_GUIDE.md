# 中医问诊管理系统 — 开发步骤指南

> 基于 `PROJECT_CONTEXT.md`，面向任何 agent 或开发者的逐步开发指南。
> 要求：代码规范、可扩展、每步可独立验证。
> 最后更新：2026-03-20

---

## 代码规范总则

### Python 后端规范
- Python 3.10+，类型注解（Type Hints）覆盖所有函数参数和返回值
- Pydantic v2 Schema 做请求/响应校验，与 ORM Model 严格分离
- SQLAlchemy 2.0 风格（使用 `Mapped`、`mapped_column`）
- 路由按资源拆分到 `routers/` 目录，每个文件一个 `APIRouter`
- 统一错误处理：自定义异常类 + 全局 exception handler，不直接 raise HTTPException
- 环境变量通过 `.env` + `pydantic-settings` 管理，不硬编码任何配置
- 日志使用 Python `logging` 模块，不用 `print`
- 密码使用 `passlib[bcrypt]` 哈希，JWT token 使用 `python-jose`

### Vue 前端规范
- Vue 3 Composition API（`<script setup lang="ts">` 语法）
- TypeScript 严格模式（`strict: true`）
- 组件命名：PascalCase，文件名与组件名一致
- API 请求封装到 `src/api/` 目录，axios 实例统一配置 baseURL、请求拦截器（自动带 token）、响应拦截器（统一错误处理）
- 状态管理：Pinia（store 按业务模块拆分）
- 路由：Vue Router 4，路由守卫做登录校验（医师端和患者端各自独立守卫逻辑）
- 样式：CSS 变量统一管理主题色，全局 `variables.css` 定义，禁止在组件内硬编码颜色值
- 响应式：Element Plus 栅格 + CSS media query，医师端支持桌面/平板/手机三种宽度

### 可扩展性设计
- 后端 API 路径统一前缀 `/api/v1/`，方便未来 v2 版本共存
- 数据库 CRUD 操作封装为独立工具函数（`crud/` 目录），路由层不直接写 SQL
- 症状/部位等配置数据抽离为 `data/symptom_config.json`，前端通过 API 获取，不硬编码
- 前端 API baseURL 通过 `.env` 环境变量配置，一行切换开发/生产环境
- 预留 `wx_openid` 字段和 `/api/v1/auth/wechat` 路由接口，V2 直接启用无需改表结构
- `doctors` 表包含 `role` 字段，V1 先实现 `doctor/admin`
- `doctor_id` 相关字段可在 V1 保留为 V2 多医师预留，不在前端流程中暴露

---

## 阶段一：后端基础搭建

### Step 1.1 — 项目初始化与配置

创建后端完整目录结构：

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口，注册所有 router，配置 CORS
│   ├── config.py            # pydantic-settings 配置类，读取 .env
│   ├── database.py          # 数据库引擎、SessionLocal、Base 声明
│   ├── dependencies.py      # 公共依赖：get_db、get_current_doctor（JWT验证）
│   ├── exceptions.py        # 自定义异常类 + 全局 exception handler 注册
│   ├── models/              # SQLAlchemy ORM 模型（每张表一个文件）
│   │   ├── __init__.py      # 统一导出所有 Model，确保建表时全部加载
│   │   ├── doctor.py        # 医师账号表
│   │   ├── patient.py       # 患者表
│   │   ├── patient_history.py
│   │   ├── visit.py
│   │   ├── symptom.py
│   │   ├── medical_record.py
│   │   ├── lab_result.py
│   │   ├── schedule.py
│   │   ├── schedule_override.py
│   │   └── appointment.py
│   ├── schemas/             # Pydantic 请求/响应 Schema（每张表一个文件）
│   │   ├── __init__.py
│   │   ├── auth.py          # 登录请求/响应 Token Schema
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── patient_history.py
│   │   ├── visit.py
│   │   ├── symptom.py
│   │   ├── medical_record.py
│   │   ├── lab_result.py
│   │   ├── schedule.py
│   │   └── appointment.py
│   ├── crud/                # 数据库 CRUD 操作封装（每张表一个文件）
│   │   ├── __init__.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── patient_history.py
│   │   ├── visit.py
│   │   ├── symptom.py
│   │   ├── medical_record.py
│   │   ├── lab_result.py
│   │   ├── schedule.py
│   │   └── appointment.py
│   └── routers/             # API 路由（每个资源一个文件）
│       ├── __init__.py
│       ├── auth.py          # 医师登录/患者手机号+姓名登录/JWT刷新
│       ├── doctors.py       # 医师账号管理
│       ├── patients.py      # 患者信息 CRUD
│       ├── visits.py        # 就诊记录
│       ├── symptoms.py      # 症状采集
│       ├── medical_records.py
│       ├── lab_results.py
│       ├── schedules.py     # 排班设置
│       ├── appointments.py  # 预约管理
│       ├── analysis.py      # 图表数据接口
│       ├── backup.py        # 数据备份导出
│       └── config.py        # 配置数据（症状列表等）
├── data/
│   └── symptom_config.json  # 12个部位 + 对应症状标签
├── .env                     # 环境变量（不提交到 git）
├── .env.example             # 环境变量示例（提交到 git）
├── requirements.txt
└── Procfile                 # Render 部署配置
```

`.env` 需包含的变量：
```
DATABASE_URL=sqlite:///./zhongyi.db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

**验证点**：`uvicorn app.main:app --reload` 启动成功，访问 `http://localhost:8000/docs` 看到 Swagger 页面。

---

### Step 1.2 — 认证（Auth）

认证体系优先实现，后续所有医师端接口依赖此步骤：

- 密码存储：`passlib[bcrypt]` 哈希，不存明文
- JWT token：`python-jose[cryptography]`，token 包含 `doctor_id` + `role`
- `dependencies.py` 中实现 `get_current_doctor`：从请求 Header 取 Bearer token → 解码 → 查数据库 → 返回 doctor 对象
- 初始化脚本：`python -m app.init_db` 创建默认管理员账号和默认医师账号

API：
```
POST /api/v1/auth/doctor/login     # 医师账号密码登录，返回 JWT token
POST /api/v1/auth/patient/login    # 患者手机号+姓名登录，返回 patient_id（无JWT）
POST /api/v1/auth/wechat           # 预留：V2微信openid登录
```

**验证点**：`POST /api/v1/auth/doctor/login` 传正确账号密码返回 token，错误密码返回 401。

---

### Step 1.3 — 数据库模型（10 张表）

按 `PROJECT_CONTEXT.md` 第五节建表。关键要点：

- 所有表使用自增整数 `id` 主键
- 时间字段使用 `DateTime`，`server_default=func.now()`
- 外键关系定义 `relationship`，适当设置 `cascade`
- 索引：`patients.phone` 唯一索引；`appointments(appointment_date, time_slot)` 联合唯一约束
- `visits.visit_number`：后端在 `crud/visit.py` 中自动计算（该患者历史记录数 + 1）
- `visits.visit_date`：记录就诊日期，后端校验症状提交时 `date.today() == visit.visit_date`
- `visits.status`：支持 `待签到/待接诊/已完成/已作废`
- `appointments` / `schedules` / `schedule_overrides` 可保留 `doctor_id` 作为 V2 多医师预留字段；V1 固定绑定唯一医师

**验证点**：启动时 `Base.metadata.create_all()` 执行，`zhongyi.db` 中存在全部 10 张表。

---

### Step 1.4 — Pydantic Schema

每张表创建 3 个 Schema：
- `XxxCreate`：创建请求体（必填字段）
- `XxxUpdate`：更新请求体（所有字段 `Optional`）
- `XxxResponse`：响应体（含 `id`、`created_at` 等）

关键 Schema 约束：
- `SymptomRecordCreate.body_part`：`Literal["头部","面部","颈部","肩部","胸部","腹部","腰部","背部","上肢","下肢","足部","全身"]` 枚举约束
- `SymptomRecordCreate.severity`：`conint(ge=1, le=10)` 范围约束
- `MedicalRecordCreate.treatment_type`：`Literal["中药","针灸","推拿","艾灸","其他"]`
- `AppointmentCreate`：`appointment_date` 不能是过去的日期，不能超过今天起 7 天
- `AppointmentCancelRequest`：患者取消时后端校验 `appointment_date > date.today()`（必须提前1天）

**验证点**：body_part 传非法值返回 422，severity 传 11 返回 422。

---

### Step 1.5 — CRUD 工具函数

每个 `crud/xxx.py` 封装标准操作：
```python
def create_xxx(db: Session, schema: XxxCreate) -> Xxx
def get_xxx(db: Session, id: int) -> Xxx | None
def get_xxx_list(db: Session, skip: int = 0, limit: int = 20, **filters) -> list[Xxx]
def update_xxx(db: Session, id: int, schema: XxxUpdate) -> Xxx
def delete_xxx(db: Session, id: int) -> bool
```

特殊业务逻辑（关键）：
- `crud/patient.py`：`get_by_phone_and_name(db, phone, name)` — 按手机号+姓名识别患者
- `crud/visit.py`：`create_visit()` 自动计算并写入 `visit_number`；校验同一患者同一天只能有一条就诊记录
- `crud/appointment.py`：
  - `get_available_slots(db, date)` — 合并诊所唯一医师的排班+临时调整+已预约，返回可用时段列表
  - `cancel_by_patient(db, apt_id)` — 校验是否超过截止时间（就诊前1天）
  - `cancel_by_doctor(db, apt_id)` — 无时间限制
- `crud/schedule.py`：`get_effective_schedule(db, date)` — 优先取临时调整，否则取固定排班
- `crud/medical_record.py`：保存病历后自动把本次 `visit` 和关联 `appointment` 标记为已完成

**验证点**：单独调用各 CRUD 函数无报错，`get_available_slots` 返回正确的可用时段。

---

### Step 1.6 — 完整 API 路由

所有接口路径，前缀统一 `/api/v1/`：

```
# 认证
POST   /api/v1/auth/doctor/login              # 医师账号密码登录
POST   /api/v1/auth/patient/login             # 患者手机号+姓名登录

# 管理员工具
PUT    /api/v1/doctors/{id}/reset-password    # 重置默认医师密码 [admin]
PUT    /api/v1/patients/merge                 # 合并患者档案 [admin]

# 患者（医师端需 JWT，患者端用 patient_id 查询自己）
POST   /api/v1/patients                        # 创建患者（患者自填或医师代填）
GET    /api/v1/patients                        # 患者列表，支持姓名/手机号搜索 [需JWT]
GET    /api/v1/patients/{id}                   # 患者详情
PUT    /api/v1/patients/{id}                   # 更新患者基本信息
POST   /api/v1/patients/{id}/history           # 添加既往史
GET    /api/v1/patients/{id}/history           # 查看既往史

# 就诊记录
POST   /api/v1/visits                          # 创建就诊（患者扫码 or 医师手动）
GET    /api/v1/visits                          # 就诊列表（按日期/状态/患者筛选）[需JWT]
GET    /api/v1/visits/today                    # 今日就诊列表（含统计数字）[需JWT]
GET    /api/v1/visits/{id}                     # 就诊详情
PUT    /api/v1/visits/{id}/check-in           # 到店签到（待签到→待接诊）
PUT    /api/v1/visits/{id}/status              # 更新就诊状态（待接诊→已完成）[需JWT]

# 症状（仅限就诊当天提交）
POST   /api/v1/visits/{id}/symptoms            # 批量提交症状（后端校验当天）
GET    /api/v1/visits/{id}/symptoms            # 查看症状列表

# 病历（医师填写）
POST   /api/v1/visits/{id}/medical-record      # 创建病历 [需JWT]
PUT    /api/v1/medical-records/{id}            # 更新病历 [需JWT]
GET    /api/v1/visits/{id}/medical-record      # 查看病历

# 检验指标
POST   /api/v1/visits/{id}/lab-results         # 添加检验指标 [需JWT]
GET    /api/v1/patients/{id}/lab-results       # 患者所有检验指标

# 排班管理
GET    /api/v1/schedules                        # 查看排班设置
PUT    /api/v1/schedules                        # 批量更新排班设置 [需JWT]
POST   /api/v1/schedule-overrides              # 添加临时调整 [需JWT]
DELETE /api/v1/schedule-overrides/{id}         # 删除临时调整 [需JWT]

# 预约
GET    /api/v1/appointments/available-slots    # 可预约时段 ?date=2026-03-20
POST   /api/v1/appointments                    # 患者创建预约
GET    /api/v1/appointments                    # 预约列表（支持日期/状态筛选）[需JWT]
GET    /api/v1/patients/{id}/appointments      # 患者自己的预约记录
PUT    /api/v1/appointments/{id}/cancel        # 取消预约（患者/医师均可，校验规则不同）
PUT    /api/v1/appointments/{id}/no-show       # 当日营业结束后标记爽约 [需JWT]

# 分析图表
GET    /api/v1/analysis/patients/{id}/symptom-trend   # 症状趋势折线图数据
GET    /api/v1/analysis/patients/{id}/radar           # 雷达图数据（首诊vs当前）
GET    /api/v1/analysis/patients/{id}/timeline        # 治疗时间轴数据
GET    /api/v1/analysis/patients/{id}/lab-trend       # 检验指标趋势数据

# 备份导出
GET    /api/v1/backup/export-excel             # 导出全部数据为 Excel [需JWT]
GET    /api/v1/backup/download-db              # 下载 zhongyi.db 文件 [需JWT]
GET    /api/v1/backup/patients/{id}/export     # 导出单个患者病历 [需JWT]

# 配置
GET    /api/v1/config/symptoms                 # 12个部位+症状标签配置
GET    /api/v1/qrcode                          # 生成患者端 H5 二维码图片
```

**CORS 配置**：`main.py` 中配置，允许来自 `.env` 中 `CORS_ORIGINS` 的跨域请求。

**验证点**：所有接口在 `/docs` 可调通；`[需JWT]` 接口不带 token 返回 401；症状接口在非就诊当天提交返回 400。

---

### Step 1.7 — 症状配置数据

创建 `data/symptom_config.json`，12 个部位完整定义：

```json
{
  "body_parts": [
    { "key": "head",      "label": "头部",  "symptoms": ["头痛","偏头痛","头晕","头胀","头重","头皮麻木"] },
    { "key": "face",      "label": "面部",  "symptoms": ["目眩","眼干","耳鸣","耳聋","鼻塞","口干","口苦","牙痛","面部浮肿"] },
    { "key": "neck",      "label": "颈部",  "symptoms": ["颈部僵硬","颈痛","咽痛","咽干","吞咽困难","颈部淋巴结肿大"] },
    { "key": "shoulder",  "label": "肩部",  "symptoms": ["肩痛","肩周炎","肩部沉重","肩部活动受限"] },
    { "key": "chest",     "label": "胸部",  "symptoms": ["胸闷","胸痛","心悸","气短","咳嗽","咳痰","两肋胀痛"] },
    { "key": "abdomen",   "label": "腹部",  "symptoms": ["胃痛","腹胀","腹痛","恶心","呕吐","食欲不振","便秘","腹泻"] },
    { "key": "waist",     "label": "腰部",  "symptoms": ["腰痛","腰酸","腰部沉重","腰部活动受限"] },
    { "key": "back",      "label": "背部",  "symptoms": ["背痛","背部发凉","背部沉重","脊柱疼痛"] },
    { "key": "upper_limb","label": "上肢",  "symptoms": ["手指发麻","手指冰凉","手臂酸痛","关节痛","握力减弱","手抖","手指冒凉气"] },
    { "key": "lower_limb","label": "下肢",  "symptoms": ["腿软","膝痛","小腿抽筋","下肢浮肿","腿部发凉","静脉曲张"] },
    { "key": "foot",      "label": "足部",  "symptoms": ["足跟痛","脚趾麻木","足部冰凉","足底疼痛"] },
    { "key": "whole_body","label": "全身",  "symptoms": ["畏寒","发热","乏力","盗汗","自汗","失眠","多梦","水肿","体重减轻"] }
  ]
}
```

`/api/v1/config/symptoms` 直接读取并返回此 JSON。

**验证点**：接口返回完整 12 个部位，每个部位有症状列表。

---

## 阶段二：患者端 H5 开发

### Step 2.1 — 项目初始化

```bash
npm create vite@latest patient-h5 -- --template vue-ts
cd patient-h5
npm install vant@4 vue-router@4 pinia axios
```

目录结构：

```
patient-h5/src/
├── api/
│   ├── index.ts          # axios 实例（baseURL 从 import.meta.env.VITE_API_URL 读取）
│   ├── auth.ts           # 患者手机号+姓名登录
│   ├── patient.ts        # 患者信息 CRUD
│   ├── visit.ts          # 就诊记录
│   ├── symptom.ts        # 症状提交
│   ├── appointment.ts    # 预约相关
│   └── config.ts         # 获取症状配置
├── stores/
│   └── patient.ts        # 患者状态（Pinia）：patient_id、name、visit_count
├── router/
│   └── index.ts          # 路由配置 + 守卫（无 patient_id 跳转 Login）
├── views/
│   ├── Login.vue          # 手机号+姓名登录
│   ├── PatientInfo.vue    # 基本信息填写/编辑
│   ├── Appointment.vue    # 在线预约（日期+时段）
│   ├── SymptomForm.vue    # 结构化症状采集（核心页面）
│   └── MyRecords.vue      # 我的就诊记录 + 预约记录
├── components/
│   ├── BodyPartSelector.vue   # 人体 SVG 部位选择器
│   ├── SymptomChips.vue       # 症状标签勾选
│   ├── SeveritySlider.vue     # 严重程度卡片（含滑块/时间/细节）
│   └── TimeSlotPicker.vue     # 预约时段选择网格
├── styles/
│   └── variables.css          # CSS 主题变量
├── .env.development           # 开发环境 API 地址
├── .env.production            # 生产环境 API 地址
├── App.vue
└── main.ts
```

全局 CSS 变量（`variables.css`）：

```css
:root {
  --color-primary: #5DB391;
  --color-primary-light: #E8F5E9;
  --color-primary-bg: #F0F7F4;
  --color-symptom: #EF9A9A;
  --color-symptom-light: #FFEBEE;
  --color-bg: #FAFAFA;
  --color-card: #FFFFFF;
  --color-text: #333333;
  --color-text-secondary: #999999;
  --color-border: #EEEEEE;
  --color-success: #81C784;
  --color-error: #E57373;
  --radius-card: 16px;
  --radius-btn: 999px;
  --shadow-card: 0 2px 8px rgba(0,0,0,0.06);
}
```

**验证点**：`npm run dev` 启动，首页空白无报错，CSS 变量生效。

---

### Step 2.2 — 登录页 (Login.vue)

- 手机号输入框（11位数字格式校验）+ 姓名输入框
- "进入问诊"按钮 → `POST /api/v1/auth/patient/login`
- 返回 `{ exists: true, patient_id, name, visit_count }` → 存 Pinia → 跳转首页
- 返回 `{ exists: false }` → 跳转 PatientInfo 填写基本信息
- `patient_id` 存 `localStorage`，下次打开自动登录跳过此页

**验证点**：新患者 → 跳 PatientInfo；已有患者 → 跳首页，显示正确姓名和就诊次数。

---

### Step 2.3 — 基本信息页 (PatientInfo.vue)

- 姓名（必填）、性别单选（男/女）、出生日期日期选择器
- 既往病史：Vant 标签多选（糖尿病/高血压/心脏病/肝病/肾病/无 + 自定义输入）
- 过敏史：文本输入
- 外部就诊史（可展开）：就诊机构、治疗方式、持续时间、效果及副作用
- 提交 → `POST /api/v1/patients` 创建档案 → 跳转预约页
- 非首次进入时（从"我的记录"进入）可编辑回显

**验证点**：提交后数据库 patients 表有记录，再次打开可回显。

---

### Step 2.4 — 预约页 (Appointment.vue)

- 顶部横向日期选择器（今天起 7 天，今天高亮）
- 切换日期 → 调 `GET /api/v1/appointments/available-slots?date=xxx` 获取时段
- 时段网格展示：
  - 白色边框：可预约
  - 绿色填充：已选中
  - 灰色不可点：已约满或休息
- 当天剩余时段需额外校验截止时间（如提前1小时）
- 下方已选时段确认卡片：日期 + 时段 + 确认预约按钮
- 确认 → `POST /api/v1/appointments` → 成功提示 → 跳转首页
- 不提供“直接改预约”入口，如需改期，只能先取消再重约

**验证点**：选日期 → 时段正确显示 → 预约成功 → appointments 表有记录 → 再选同一时段已变灰。

---

### Step 2.5 — 症状填写页 (SymptomForm.vue)

**进入条件**：后端校验今天有就诊记录（`visit.visit_date == today`），否则提示"今日无就诊安排"。

核心子组件：

1. **BodyPartSelector 组件**
   - SVG 人体正面图（默认显示）+ 背面图（切换按钮）
   - 12 个可点击热区（`<path>` 或 `<rect>` 标签），`id` 对应 `body_part key`
   - 点击选中 → 填充浅珊瑚色 `#FFEBEE`，描边 `#EF9A9A`
   - 已选部位以标签形式列在图下方，可点 × 取消

2. **SymptomChips 组件**
   - 从 `/api/v1/config/symptoms` 获取配置，按已选部位过滤显示
   - 选中 → 浅珊瑚色填充白字；未选中 → 白底灰边
   - "自定义症状"输入框 + 添加按钮

3. **SeveritySlider 组件**（每个已选症状一张展开卡片）
   - 症状名称标题（珊瑚色）
   - 严重程度滑块 1-10（珊瑚色轨道和滑块）
   - 持续时间下拉（今天/2-3天/一周内/半月内/一个月/一月以上）
   - 位置细节可选：左侧/右侧/双侧/全部（部分症状适用）
   - 补充描述文本框

4. 底部绿色提交按钮 → `POST /api/v1/visits/{id}/symptoms` 批量提交 → 成功跳转"我的记录"

**验证点**：选部位 → 症状动态加载 → 打分 → 提交 → symptom_records 表有记录 → visit.symptom_submitted_at 有值。

---

### Step 2.6 — 我的记录页 (MyRecords.vue)

- Tab 切换：就诊记录 | 预约记录
- **就诊记录 Tab**：
  - 顶部患者信息小卡片（头像、姓名、年龄、总就诊次数）
  - 时间轴列表，每条显示：第N次就诊、日期、状态标签（待接诊绿/已完成灰）、症状摘要
  - 点击展开：显示医师姓名、治疗方式、简短医嘱/治疗结果摘要
  - 不显示完整病历、辨证思路、处方全文、医师备注
- **预约记录 Tab**：
  - 卡片列表：预约日期、时段、状态（待就诊/已完成/已取消）
  - 状态为"待就诊"且距就诊日期 > 1天 → 显示"取消预约"按钮
  - 状态为"待就诊"且当天 → 不显示取消按钮，显示"今日就诊"提示
- 下拉刷新

**验证点**：就诊记录和预约记录数据正确，取消按钮在当天不显示，取消后状态同步更新。

---

## 阶段三：医师端 Web 后台开发

### Step 3.1 — 项目初始化

```bash
npm create vite@latest doctor-admin -- --template vue-ts
cd doctor-admin
npm install element-plus @element-plus/icons-vue vue-router@4 pinia axios echarts vue-echarts
```

目录结构：

```
doctor-admin/src/
├── api/
│   ├── index.ts           # axios 实例（自动携带 JWT token）
│   ├── auth.ts
│   ├── patients.ts
│   ├── visits.ts
│   ├── medicalRecords.ts
│   ├── appointments.ts
│   ├── schedules.ts
│   ├── analysis.ts
│   └── backup.ts
├── stores/
│   └── auth.ts            # 医师登录态（token、doctor 信息）
├── router/
│   └── index.ts           # 路由 + 鉴权守卫（无 token 跳 Login）
├── views/
│   ├── Login.vue
│   ├── Dashboard.vue
│   ├── PatientList.vue
│   ├── PatientDetail.vue
│   ├── MedicalRecord.vue
│   ├── AppointCalendar.vue
│   ├── ScheduleSettings.vue
│   ├── Analysis.vue
│   └── DataBackup.vue
├── components/
│   ├── layout/
│   │   ├── AppLayout.vue      # 整体框架（侧边栏 + 内容区）
│   │   └── SideNav.vue        # 左侧导航菜单
│   └── charts/
│       ├── SymptomLineChart.vue
│       ├── SymptomRadar.vue
│       ├── TreatmentTimeline.vue
│       └── LabTrendChart.vue
├── styles/
│   └── variables.css
├── .env.development
├── .env.production
├── App.vue
└── main.ts
```

**验证点**：`npm run dev` 启动，路由守卫正常拦截，跳转 Login 页。

---

### Step 3.2 — 医师登录页 (Login.vue) + 布局

**Login.vue**：
- 用户名 + 密码输入框 + 登录按钮
- `POST /api/v1/auth/doctor/login` → 返回 JWT token → 存 Pinia + localStorage → 跳转 Dashboard
- 错误提示：账号或密码错误

**AppLayout + SideNav**：
- 左侧固定侧边栏（宽 240px）：Logo 区域 + 导航项 + 底部医师信息/退出
- 导航项：今日就诊 / 患者管理 / 预约管理 / 数据分析 / 数据备份
- 响应式：`< 768px` 侧边栏收起，顶部出现汉堡菜单按钮
- 右侧内容区：`<router-view>`

**验证点**：登录成功跳 Dashboard；刷新页面 token 持久，不重新登录；侧边栏在窄屏自动收起。

---

### Step 3.3 — 今日就诊 (Dashboard.vue)

- 顶部统计卡片：今日预约 / 待接诊 / 已完成 / 今日新患者 / 今日复诊患者
  - 调 `GET /api/v1/visits/today` 获取所有数据
- 列表默认按实际签到/创建时间排序
- **待接诊表格**：
  - 列：姓名、性别、年龄、第N次就诊、预约时间、主要症状（最多2个）、症状状态（已提交绿/未提交灰）、操作
  - "开始接诊"按钮 → 跳转 `MedicalRecord.vue`
- **手动创建就诊**按钮：
  - 弹出搜索框，按姓名或手机号搜索现有患者
  - 选中患者 → 创建当天就诊记录
  - 找不到患者 → 创建新患者（医师代填基本信息）
- **已完成表格**：操作列改为"查看详情"

**验证点**：统计数字准确，手动创建就诊后出现在待接诊列表，状态变更后两个列表实时更新。

---

### Step 3.4 — 患者管理 (PatientList + PatientDetail)

**PatientList.vue**：
- 顶部搜索框（姓名 / 手机号，实时调用 `GET /api/v1/patients?search=xxx`）
- 表格列：姓名、性别、年龄、手机号、总就诊次数、最近就诊日期、操作（查看详情）
- Element Plus 分页组件，每页 20 条

**PatientDetail.vue**：
- 顶部患者信息卡片：头像占位、姓名/性别/年龄、手机号、首诊日期、总就诊次数、既往病史标签
- 外部就诊史折叠展示
- 右上角：编辑信息按钮（弹抽屉）/ 导出档案按钮
- V1 为单医师模式，`doctor` 可直接查看本诊所患者的全部历史
- Tab 切换（Element Plus Tabs）：
  - **就诊记录**：时间轴组件，每条可展开，展示症状列表 + 病历内容
  - **数据分析**：嵌入 4 个 ECharts 图表组件（见 Step 3.7）
  - **检验指标**：表格展示所有 lab_results，按时间倒序

**验证点**：搜索过滤正确，详情页所有数据正常显示，Tab 切换无白屏。

---

### Step 3.5 — 撰写病历 (MedicalRecord.vue)

左右分栏布局（`< 768px` 切换为上下布局）：

**左栏（60%）病历表单**：
- 治疗方式：`el-checkbox-group`（中药/针灸/推拿/艾灸/其他），可多选
- 根据勾选内容动态显示：
  - 勾"中药" → 显示"处方"文本域（V1纯文字）
  - 勾"针灸" → 显示"穴位"标签输入（`el-tag` + 输入框，回车添加，× 删除）
- 舌诊（文本输入，如：舌淡红苔薄白）
- 脉诊（文本输入，如：脉沉细）
- 体征观察（文本域，如：颜面发黑、痰核）
- 诊断（文本域）
- 辨证思路/治疗策略（文本域）
- 治疗方案（文本域）
- 备注（文本域）
- 底部：保存病历按钮（绿色）
- 保存成功后自动将本次 `visit` 与关联 `appointment` 更新为“已完成”
- 已提交病历普通医师不可再改，仅 `admin` 可修改

**右栏（40%）患者本次症状**（只读，从 visit 关联数据获取）：
- 每个症状一张小卡片：部位 + 症状名 + 严重程度条（珊瑚色）+ 持续时间
- 患者补充描述文字
- 历史症状趋势迷你折线图（最近5次严重程度）

**验证点**：保存病历 → 刷新数据不丢失 → 患者端"我的记录"仅显示治疗结果摘要和简短医嘱。

---

### Step 3.6 — 预约管理 (AppointCalendar + ScheduleSettings)

**AppointCalendar.vue**（默认显示页）：
- Tab：预约日历 / 时段设置 / 预约列表
- 预约日历 Tab：
  - WeekCalendar 组件，显示诊所唯一医师本周 7 天 × 所有时段的网格
  - 格子颜色：绿色背景 + 患者姓名 = 已预约；白色 = 可预约；浅灰 = 休息/不可约；红色文字 = 已取消
  - 点击已预约格子 → `el-popover` 弹出：患者姓名、手机号、就诊次数、[查看详情][取消预约]
  - 上/下周切换导航
- 预约列表 Tab：表格形式显示所有预约，支持按日期/状态筛选
- 营业结束后可将未到诊记录标记为“爽约”

**ScheduleSettings.vue**（时段设置 Tab 内容）：
- 每周排班表格：周一~周日，每行含：上班开关、上午时段（开始-结束）、下午时段（开始-结束）
- 时段间隔单选：30分钟 / 45分钟 / 60分钟
- 临时调整区：日期选择器 → 设为休息日 / 修改该日时段；已有调整列表可删除
- 预约规则：提前预约天数（数字输入，默认7）；患者取消截止：就诊前1天（固定，不可改）
- 若修改后与已有预约冲突，后端自动取消冲突预约，前端需给出明确提示

**验证点**：设置排班 → 患者端可预约时段正确；医师取消预约 → 格子变红色文字 → 患者端预约记录状态同步。

---

### Step 3.7 — 数据分析 (Analysis.vue)

4 个 ECharts 图表，2×2 网格布局，接受路由参数 `patient_id`：

1. **SymptomLineChart**（症状严重程度变化折线图）
   - 数据来源：`GET /api/v1/analysis/patients/{id}/symptom-trend`
   - X 轴：第1次～第N次就诊；Y 轴：严重程度 0-10
   - 每个症状一条线，自动分配不同颜色；图例可点击显示/隐藏单条线

2. **SymptomRadar**（症状雷达图）
   - 数据来源：`GET /api/v1/analysis/patients/{id}/radar`
   - 首诊（红色）vs 当前（绿色）两个多边形，面积越小改善越明显

3. **TreatmentTimeline**（治疗时间轴）
   - 数据来源：`GET /api/v1/analysis/patients/{id}/timeline`
   - 垂直时间轴：每次就诊日期 + 关键诊断/治疗摘要

4. **LabTrendChart**（检验指标趋势）
   - 数据来源：`GET /api/v1/analysis/patients/{id}/lab-trend`
   - 柱状图，颜色随数值接近正常值从红到绿渐变；带参考值水平线

**验证点**：≥3次就诊的患者图表正常渲染；无数据时显示"暂无数据"空状态；图表随窗口大小自适应。

---

### Step 3.8 — 数据备份 (DataBackup.vue)

- "导出全部数据 Excel"按钮 → `GET /api/v1/backup/export-excel` → 触发文件下载
- "下载数据库备份"按钮 → `GET /api/v1/backup/download-db` → 下载 `zhongyi.db`
- "按患者导出病历"：搜索患者 → 选中 → `GET /api/v1/backup/patients/{id}/export` → 下载
- 页面顶部提示："建议每周定期备份，备份文件请妥善保存"
- 显示数据库最后更新时间

**验证点**：Excel 文件可正常打开，数据完整；db 文件可用 DB Browser 打开查看所有表。

---

## 阶段四：联调与优化

### Step 4.1 — 完整流程联调

联调清单：
- 患者端：手机号+姓名登录 → 填信息 → 预约 → 到店签到 → 当天填症状 → 查就诊记录摘要 → 查预约记录 → 取消预约（提前1天/当天两种情况）
- 医师端：登录 → 今日列表 → 接诊 → 写病历（中药/针灸两种） → 看分析图表 → 导出备份
- 联动校验：患者提交症状 → 医师端待接诊列表症状状态标记变绿；医师写完病历 → 患者端仅显示治疗结果摘要和简短医嘱，不显示完整病历

### Step 4.2 — 边界情况处理

- 患者当天无预约时进入症状填写页：显示"今日无就诊安排，请先预约"
- 重复预约同一时段：后端返回 400，前端友好提示
- 患者在就诊当天尝试取消预约：前端隐藏取消按钮，后端也做校验拦截
- 医师修改排班导致时段冲突：后端自动取消冲突预约，前端提示受影响患者
- 未签到患者不进入待接诊队列；营业结束后仍未到诊可标记“爽约”
- 医师查看无就诊记录的新患者分析页：显示"暂无数据，至少需要2次就诊"
- 网络断开：axios 拦截器统一提示"网络异常，请检查网络连接"

### Step 4.3 — 响应式测试

- 医师端：1920px / 1366px / 768px / 375px 四种宽度
- 患者端：375px (iPhone SE) / 390px (iPhone 14) / 428px (iPhone 14 Plus) / 主流安卓 360px

### Step 4.4 — 性能优化

- 患者列表分页（每页20条）
- ECharts 组件 `v-if` 懒加载，只在 Tab 激活时渲染
- 症状配置 JSON 前端缓存（localStorage），不每次请求

---

## 阶段五：部署上线

### Step 5.1 — 后端部署到 Render

- 添加 `Procfile`：`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- 添加 `render.yaml`：声明服务类型、构建命令、环境变量
- `requirements.txt` 确保所有依赖版本锁定
- 推送到 GitHub → Render 关联仓库 → 自动构建部署
- Render 控制台配置环境变量：`SECRET_KEY`、`CORS_ORIGINS`
- 开启 Persistent Disk 挂载路径为 `/data`，数据库路径改为 `/data/zhongyi.db`

### Step 5.2 — 前端部署

- 患者端 + 医师端分别在 `.env.production` 配置后端 API 地址
- `npm run build` 生成 `dist/` 目录
- 推荐：让 FastAPI 直接 serve 前端产物（单服务部署，最简单，无需额外配置）

  ```python
  # main.py 末尾添加
  app.mount("/", StaticFiles(directory="patient-h5/dist", html=True), name="patient")
  app.mount("/admin", StaticFiles(directory="doctor-admin/dist", html=True), name="admin")
  ```

### Step 5.3 — 生成诊所二维码

- 后端接口 `GET /api/v1/qrcode` 使用 `qrcode` 库生成患者端 URL 的二维码图片（PNG）
- 医师后台 DataBackup 页面提供"下载二维码"按钮
- 下载后可打印 A4 纸贴在诊所前台

### Step 5.4 — 编写 README

包含：
- 项目简介和功能截图
- 本地开发启动步骤（三个服务：backend / patient-h5 / doctor-admin）
- 部署到 Render 的步骤
- 环境变量说明（对照 `.env.example`）
- V1→V2 升级路径说明

---

## 开发顺序总览

```
阶段一 后端（约 40% 工作量）
  1.1 项目初始化与配置
  1.2 医师认证（Auth + JWT）        ← 优先！其他接口依赖此步
  1.3 数据库 10 张表 ORM 模型
  1.4 Pydantic Schema（含业务校验）
  1.5 CRUD 工具函数（含预约规则）
  1.6 完整 API 路由
  1.7 症状配置 JSON + 接口

阶段二 患者端 H5（约 25% 工作量）
  2.1 项目初始化 + 主题 CSS 变量
  2.2 登录页（手机号识别新老患者）
  2.3 基本信息页
  2.4 症状填写页（核心，含人体SVG）
  2.5 预约页
  2.6 我的记录页（含取消预约逻辑）

阶段三 医师端 Web（约 25% 工作量）
  3.1 项目初始化 + 主题配置
  3.2 登录页 + 整体响应式布局
  3.3 今日就诊 Dashboard（含手动创建）
  3.4 患者列表 + 患者详情
  3.5 撰写病历（左右分栏）
  3.6 预约管理（周历 + 排班设置）
  3.7 数据分析（4个ECharts图表）
  3.8 数据备份导出

阶段四 联调优化（约 5% 工作量）
  4.1 完整流程联调
  4.2 边界情况处理
  4.3 响应式测试
  4.4 性能优化

阶段五 部署上线（约 5% 工作量）
  5.1 后端部署 Render + 持久化磁盘
  5.2 前端构建 + 静态文件 serve
  5.3 生成诊所二维码
  5.4 编写 README
```

**每个 Step 完成后都有明确的验证点，确保该步骤功能正确后再进入下一步。**
