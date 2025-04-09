# 科研管理平台 - 后端项目

## 一、项目介绍
本项目是一个科研管理平台的后端系统，基于Django框架开发，旨在为科研团队提供高效的管理工具。系统支持用户管理、团队管理、比赛管理等功能，帮助科研团队更好地协作和管理项目。
## 二、功能介绍
- 用户管理：支持用户注册、登录、信息管理，包括学生、教师、队长
- 团队管理：支持团队创建、成员邀请、团队管理等功能，包括团队信息更新、解散团队等。
- 比赛管理：支持比赛创建、比赛信息更新、比赛删除等功能，包括比赛成绩管理等。
- 权限管理：支持不同用户角色的权限管理，包括学生、教师和团队管理员的权限设置。

## 三、模块介绍
### 1. 用户模块
- **功能**: 用户注册、登录、信息管理
- **接口**:
  - `POST /api/user/register/`: 用户注册
    - **参数**:
      - `role`: 用户角色，可选值为 `student` 或 `teacher`
      - `username`: 用户名
      - `password`: 密码
      - `college_id`: 学院ID
      - `phone`: 手机号
      - `cn`: 学生身份证号（仅学生）
      - `team_id`: 团队ID（仅学生）
      - `email`: 邮箱（仅教师）
      - `title`: 职称（仅教师）
  - `POST /api/user/login/`: 用户登录
    - **参数**:
      - `username`: 用户名
      - `password`: 密码

### 2. 团队模块
- **功能**: 团队创建、成员邀请、团队管理
- **接口**:
  - `POST /api/team/create-team/`: 创建团队并发送邀请，只有队长可以
    - **参数**:
      - `name`: 团队名称
      - `description`: 团队描述
      - `members`: 成员列表（包含学生ID）
  - `POST /api/team/confirm-team/`: 确认团队邀请
    - **参数**:
      - `team_id`: 团队ID
      - `student_id`: 学生ID
  - `POST /api/team/invite-new-member/`: 邀请新成员，只有队长可以
    - **参数**:
      - `team_id`: 团队ID
      - `student_id`: 学生ID
  - `POST /api/team/invite-new-teacher/`: 邀请新老师，只有队长可以
    - **参数**:
      - `team_id`: 团队ID
      - `teacher_id`: 教师ID
  - `GET /api/team/myteam/`: 查看我的团队
  - `GET /api/team/allteam/`: 查看所有团队
  - `DELETE /api/team/dismiss/<int:pk>/`: 解散团队，只有队长可以
    - **参数**:
      - `pk`: 团队ID
  - `PUT /api/team/update/<int:pk>/`: 更新团队信息，只有队长可以
    - **参数**:
      - `pk`: 团队ID
      - `name`: 团队名称
      - `description`: 团队描述
  - `PUT /api/team/quit/<int:pk>/`: 退出团队
    - **参数**:
      - `pk`: 团队ID

### 3. 比赛模块
- **功能**: 比赛创建、比赛信息更新、比赛删除
- **接口**:
  - `POST /api/competition/`: 创建比赛，只有队长可以
    - **参数**:
      - `title`: 比赛名称
      - `date`: 比赛日期
      - `description`: 比赛描述
      - `score`: 比赛成绩
      - `teacher_num`: 老师数量
      - `team_id`: 团队ID
      - `file`: 证书图片
  - `PUT /api/competition/<int:pk>/`: 更新比赛信息，只有队长可以
    - **参数**:
      - `pk`: 比赛ID
      - `title`: 比赛名称
      - `date`: 比赛日期
      - `description`: 比赛描述
      - `score`: 比赛成绩
      - `teacher_num`: 老师数量
      - `file`: 证书图片
  - `DELETE /api/competition/<int:pk>/`: 删除比赛，只有队长可以
    - **参数**:
      - `pk`: 比赛ID
  - `PUT /api/competition/confirm/<int:pk>/`: 确认比赛信息
    - **参数**:
      - `pk`: 比赛ID
  - `GET /api/competition/my_competitions/`: 查看我的比赛

### 4. 学院模块
- **功能**: 学院信息管理
- **接口**:
  - `GET /api/college/`: 获取学院列表

### 5. 教师模块
- **功能**: 教师信息管理
- **接口**:
  - `GET /api/teacher/info/`: 教师信息增改查
    - **参数**:
      - `id`: 教师ID
      - `name`: 教师姓名
      - `email`: 教师邮箱
      - `title`: 教师职称

### 6. 学生模块
- **功能**: 学生信息管理
- **接口**:
  - `GET /api/student/info/`: 学生信息增改查
    - **参数**:
      - `id`: 学生ID
      - `name`: 学生姓名
      - `cn`: 学生身份证号
      - `team_id`: 学生团队ID
  - `POST /api/student/update_avatar/`: 更新学生头像
    - **参数**:
      - `avatar`: 头像图片文件（JPEG/PNG，最大5MB）

### 7. 工具模块
- **功能**: 提供系统常用的工具类
- **工具类**:
  - `minio_utils.py`: 提供与MinIO存储服务交互的工具函数，包括文件上传、删除、验证等功能。
    - `upload_competition_image_to_minio`: 上传比赛图片到MinIO并返回URL列表。
    - `delete_files_from_minio`: 从MinIO中删除指定文件。
    - `validate_image_file`: 验证图片文件的格式和大小。
  - `token_utils.py`: 提供与JWT Token相关的工具函数。
    - `generate_token`: 生成带有角色等自定义信息的JWT Token。
  - `token_auth_middleware.py`: 提供基于Token的认证中间件。
    - `TokenAuthMiddleware`: 用于验证请求中的Token，确保用户已登录。
  - `csrf_middleware.py`: 提供CSRF Token相关的中间件。
    - `NotUseCsrfTokenMiddlewareMixin`: 用于禁用CSRF Token验证。
  - `baseView.py`: 提供基础的视图类。
    - `BaseModelViewSet`: 提供基础的ModelViewSet，包含通用的异常处理和响应格式化。

## 四、使用文档
### 环境配置
1. 安装Python 3.11及以上版本
2. 安装依赖包：`pip install -r requirements.txt`
3. 配置环境：参考`.env.py`中的env，编写对应的.env
4. 运行迁移命令：`python manage.py migrate`
5. 启动开发服务器：`python manage.py runserver 127.0.0.1:8105`
