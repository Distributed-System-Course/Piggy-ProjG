BEGIN;
--
-- Create model Project
--
CREATE TABLE "project" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(150) NOT NULL,
    "description" varchar(500) NOT NULL,
    "max_group_num" integer NOT NULL,
    "max_team_member_num" integer NOT NULL,
    "project_group_id" bigint NOT NULL REFERENCES "plan" ("id") DEFERRABLE INITIALLY DEFERRED
);
--
-- Create model Student
--
CREATE TABLE "student" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "username" varchar(150) NOT NULL,
    "password" varchar(128) NOT NULL,
    "name" varchar(150) NOT NULL,
    "rank" integer NOT NULL,
    "email" varchar(150) NOT NULL,
    "resume" varchar(150) NOT NULL
);
--
-- Create model Teacher
--
CREATE TABLE "teacher" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "username" varchar(150) NOT NULL,
    "password" varchar(128) NOT NULL,
    "name" varchar(150) NOT NULL,
    "email" varchar(150) NOT NULL,
    "resume" varchar(150) NOT NULL
);
--
-- Create model Team
--
CREATE TABLE "team" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(150) NOT NULL,
    "project_id" bigint NOT NULL REFERENCES "project" ("id") DEFERRABLE INITIALLY DEFERRED,
    "project_group_id" bigint NOT NULL REFERENCES "plan" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE "team_members" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "team_id" bigint NOT NULL REFERENCES "team" ("id") DEFERRABLE INITIALLY DEFERRED,
    "student_id" bigint NOT NULL REFERENCES "student" ("id") DEFERRABLE INITIALLY DEFERRED
);
--
-- Create model TeamWish
--
CREATE TABLE "teamwish" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "priority" integer NOT NULL,
    "project_id" bigint NOT NULL REFERENCES "project" ("id") DEFERRABLE INITIALLY DEFERRED,
    "team_id" bigint NOT NULL REFERENCES "team" ("id") DEFERRABLE INITIALLY DEFERRED
);
--
-- Create model Plan
--
CREATE TABLE "plan" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(150) NOT NULL,
    "is_expired" bool NOT NULL,
    "description" varchar(500) NOT NULL
    "teacher_id" bigint NOT NULL REFERENCES "teacher" ("id") DEFERRABLE INITIALLY DEFERRED
);

---
--- ANCHOR: DB_INDEX
CREATE INDEX "project_project_group_id" ON "project" ("project_group_id");

CREATE INDEX "team_project_id" ON "team" ("project_id");
CREATE INDEX "team_project_group_id" ON "team" ("project_group_id");

CREATE UNIQUE INDEX "team_members_team_id_student_id_uniq" 
    ON "team_members" ("team_id", "student_id");
CREATE INDEX "team_members_team_id" ON "team_members" ("team_id");
CREATE INDEX "team_members_student_id" ON "team_members" ("student_id");

CREATE INDEX "teamwish_project_id" ON "teamwish" ("project_id");
CREATE INDEX "teamwish_team_id" ON "teamwish" ("team_id");

CREATE INDEX "plan_teacher_id" ON "plan" ("teacher_id");
--- ANCHOR_END: DB_INDEX
---

COMMIT;
