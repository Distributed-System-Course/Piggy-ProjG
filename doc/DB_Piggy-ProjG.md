# 项目组队系统

## 1. 需求分析

​项目组队系统主要是完成对学生信息管理、教师信息管理、学生组队管理、项目分发管理、项目匹配管理等。

​教师首先面向特定学生发布项目计划（一个项目计划中包括一批不同的项目），教师可对其发布的计划，以及计划中的所有项目进行增删改查等操作。

​学生首先按照一定要求进行组队，组队完成后以小组为单位进行项目志愿的填报，学生仅能对项目信息进行查询。

**涉及的数据**：

- 教师信息：教师编号、教师名、电话号码、教师电子邮箱、教师登陆密码；
- 学生信息：学生编号、学生姓名、学生登陆密码、学生成绩；
- 项目计划：项目计划编号、项目计划名称；
- 项目：项目编号、项目名称、项目简介、项目的人数要求
- 组队表：小组编号、小组成员、小组志愿

## 2. 概念设计

在设计项目组对系统数据库时，依据对系统做出的数据和功能的需求分析，确定要存储的有关对象的信息和各个对象的基本属性信息，还需要确定这些对象之间的相互关系。设计出概念模型如下：

![数据库 ER 图](./assets/ER-diagram.svg)

## 3. 逻辑结构设计

​逻辑结构设计是根据设计完成的概念模型，按照“实体和联系可以转换成关系”的转换规则，转换生成关系数据库管理系统支持的数据库表的数据结构。然后根据关系数据理论，对关系模式进行优化。根据以上设计的资产管理系统的概念模型和实际应用中的需要，为系统设计出的各数据表的数据结构和完整性约束条件如表所示。

```SQL
create table teacher( 
teacher_id char(7) primary key NOT NULL,
teacher_name char(20) NOT NULL,
teacher_email char(30),
teacher_key char(18) NOT NULL,
teacher_tele char(11)
 );
 
create table student(
student_id char(8) primary key NOT NULL,
student_name char(20) NOT NULL,
student_key char(18) NOT NULL,
student_score float NOT NULL
 );
 
create table project_batch( 
batch_id char(8) primary key NOT NULL,
batch_name char(20) NOT NULL,
batch_teacher_id char(7) NOT NULL, 
foreign key (batch_teacher_id) references teacher(teacher_id)
 );
 
create table project( 
project_id char(8) primary key NOT NULL,
project_batch char(8) NOT NULL, 
project_name char(20) NOT NULL,
project_min int ,
project_max int ,
project_discription char(255),
foreign key (project_batch) references project_batch(batch_id)
 );
 
 create table team(
 team_whatever char(8) primary key,
 team_id char(8)  NOT NULL,
 team_member char(8) NOT NULL,
 team_volunteer1 char(8) NOT NULL,
 team_volunteer2 char(8) NOT NULL,
 team_volunteer3 char(8) NOT NULL,
 foreign key (team_member) references student(student_id)
 );
```



