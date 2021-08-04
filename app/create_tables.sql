CREATE SEQUENCE groups_id_seq;
CREATE TABLE public.groups
(
    id integer PRIMARY KEY NOT NULL DEFAULT nextval('groups_id_seq'),
    name character(5) NOT NULL
);
ALTER TABLE public.groups
    OWNER to test_user;


CREATE SEQUENCE students_id_seq;
CREATE TABLE public.students
(
    id integer PRIMARY KEY NOT NULL  DEFAULT nextval('students_id_seq'),
    group_id integer NOT NULL,
	first_name character(100) NOT NULL,
	last_name character(100) NOT NULL
);
ALTER TABLE public.students
    OWNER to test_user;


CREATE SEQUENCE courses_id_seq;
CREATE TABLE public.courses
(
    id integer PRIMARY KEY NOT NULL DEFAULT nextval('courses_id_seq'),
	name character(100) NOT NULL,
	description character(1000) NOT NULL
);
ALTER TABLE public.courses
    OWNER to test_user;


CREATE SEQUENCE students_courses_relation_id_seq;
CREATE TABLE public.students_courses_relation
(
    id integer PRIMARY KEY NOT NULL DEFAULT nextval('students_courses_relation_id_seq'),
	student_id integer NOT NULL,
	course_id integer NOT NULL
);
ALTER TABLE public.students_courses_relation
    OWNER to test_user;