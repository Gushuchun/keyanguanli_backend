# 科研管理平台 - 后端项目

## 项目介绍
本项目是一个科研管理平台的后端系统，基于Django框架开发，旨在为科研团队提供高效的管理工具。系统支持用户管理、团队管理、比赛管理等功能，帮助科研团队更好地协作和管理项目。

## 模块介绍
### 1. 用户模块
- **功能**: 用户注册、登录、信息管理
- **接口**:
  - `POST /api/user/register/`: 用户注册
  - `POST /api/user/login/`: 用户登录

### 2. 团队模块
- **功能**: 团队创建、成员邀请、团队管理
- **接口**:
  - `POST /api/team/create-team/`: 创建团队并发送邀请，只有队长可以
  - `POST /api/team/confirm-team/`: 确认团队邀请
  - `POST /api/team/invite-new-member/`: 邀请新成员，只有队长可以
  - `POST /api/team/invite-new-teacher/`: 邀请新老师，只有队长可以
  - `POST /api/team/myteam/`: 查看我的团队
  - `POST /api/team/allteam/`: 查看所有团队
  - `delete /api/team/dismiss/<int:pk>//`: 解散团队，只有队长可以
  - `put /api/team/update/<int:pk>/`: 更新团队信息，只有队长可以

### 3. 比赛模块
- **功能**: 比赛创建、比赛信息更新、比赛删除
- **接口**:
  - `POST /api/competition/`: 创建比赛，只有队长可以
  - `PUT /api/competition/<int:pk>/`: 更新比赛信息，只有队长可以
  - `DELETE /api/competition/<int:pk>/`: 删除比赛，只有队长可以
  - `put /api/competition/confirm/<int:pk>`: 确认比赛信息
  - `put /api/competition/my_competitions/`: 查看我的比赛

### 4. 学院模块
- **功能**: 学院信息管理
- **接口**:
  - `GET /api/college/`: 获取学院列表

### 5. 教师模块
- **功能**: 教师信息管理
- **接口**:
  - `GET /api/teacher/info/`: 教师信息增改查

### 6. 学生模块
- **功能**: 学生信息管理
- **接口**:
  - `GET /api/student/info/`: 学生信息增改查

## 使用文档
### 环境配置
1. 安装Python 3.11及以上版本
2. 安装依赖包：`pip install -r requirements.txt`
3. 配置环境：参考`env_development.py`中的env，编写对应的.env
4. 运行迁移命令：`python manage.py migrate`
5. 启动开发服务器：`python manage.py runserver`

### 接口调用示例
#### 用户注册