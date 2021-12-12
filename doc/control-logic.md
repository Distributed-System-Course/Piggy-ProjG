# 程序控制逻辑

## Web 接口

用户和 Web 程序之间通过 HTTP 请求进行交互。程序为各种用户会使用到的功能，设计了对应的 URL 链接。

用户访问对应的 URL 时，运行程序的服务器将会解析对应的 URL，并执行对应的程序（在 Django 中称作 view）。服务器会返回对应的 HTTP 响应，一般情况下为一个 HTTP 页面，亦即用户所使用的应用界面。

### 项目计划相关

```python
{{#include ../PiggyProjG/piggy/urls.py:PLAN}}
```

| URL 模板 | URL 名称 | 说明 |
| --- | --- | --- |
|`plans/`  | `plans` | 查看所有计划 |
|`plan/add/` | `add_plan` | 添加一个计划（仅教师） |
|`plan/<int:plan_id>/` | `plan_detail` | 计划详情 |
|`plan/<int:plan_id>/create_team/` | `create_team` | 创建小组（仅学生） |
|`plan/<int:plan_id>/start/` | `start_plan` | 启动计划（仅教师）|
|`plan/<int:plan_id>/stop/` | `stop_plan` | 停止计划（仅教师）|
|`plan/<int:plan_id>/edit/` | `edit_plan` | 编辑计划（仅教师）|
|`plan/<int:plan_id>/del/` | `del_plan` | 删除计划（仅教师）|
|`plan/<int:plan_id>/add_project/` | `add_project` | 添加项目（仅教师）|
|`plan/<int:plan_id>/kick/<int:team_id>/` | `kick_out_team` | 移除计划中小组（仅教师）|

注：创建小组的同时，该学生亦加入该小组，因此要求该学生未参与同计划下的其他项目。

### 项目相关

```python
{{#include ../PiggyProjG/piggy/urls.py:PROJECT}}
```

| URL 模板 | URL 名称 | 说明 |
| --- | --- | --- |
| `projects/` | `projects`| 查看所有项目 |
| `projects/search/` | `search_projects`| 搜索项目 |
| `project/<int:project_id>/` | `project_detail`| 项目详情页 |
| `project/<int:project_id>/del/`| `del_project`| 删除项目（仅教师） |
| `project/<int:project_id>/edit/`| `edit_project`| 编辑项目（仅教师） |

### 教师相关

```python
{{#include ../PiggyProjG/piggy/urls.py:TEACHER}}
```

| URL 模板 | URL 名称 | 说明 |
| --- | --- | --- |
|`teachers/`|`teachers`|所有教师|
|`teacher/<int:teacher_id>/`|`teacher_detail`|教师详情页|

### 小组相关

```python
{{#include ../PiggyProjG/piggy/urls.py:TEAM}}
```

| URL 模板 | URL 名称 | 说明 |
| --- | --- | --- |
|`team/<int:team_id>/` | `team_detail` | 小组详情页|
|`team/<int:team_id>/wish/` | `team_wish` | 小组志愿填写页（仅小组中成员）|
|`team/<int:team_id>/join/` | `join_team` | 加入小组（仅学生）|
|`team/<int:team_id>/quit/` | `quit_team` | 退出小组（仅小组中成员）|

注：加入计划下的小组中即视作该学生处于该计划下。某一小组中最后一名成员退出时，小组将自动删除。

### 注册与登录相关

```python
{{#include ../PiggyProjG/piggy/urls.py:AUTH}}
```

| URL 模板 | URL 名称 | 说明 |
| --- | --- | --- |
| `login/`    |  `login`    | 用户登入 |
| `logout/`   |  `logout`   | 用户登出 |
| `register/` |  `register` | 用户注册 |

## 样式设计

使用基础 HTML 标签描述出来的界面不够直观，使用 Bootstrap 为界面应用样式。
