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
    group_id integer NOT NULL ,
	first_name  varchar(100) NOT NULL,
	last_name varchar(100) NOT NULL,
	CONSTRAINT students_group_id_fkey FOREIGN KEY (group_id)
        REFERENCES public.groups (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);
ALTER TABLE public.students
    OWNER to test_user;


CREATE SEQUENCE courses_id_seq;
CREATE TABLE public.courses
(
    id integer PRIMARY KEY NOT NULL DEFAULT nextval('courses_id_seq'),
	name varchar(100) NOT NULL,
	description text NOT NULL
);
ALTER TABLE public.courses
    OWNER to test_user;


CREATE SEQUENCE students_courses_relation_id_seq;
CREATE TABLE public.students_courses_relation
(
    id integer PRIMARY KEY NOT NULL DEFAULT nextval('students_courses_relation_id_seq'),
	student_id integer NOT NULL,
	course_id integer NOT NULL,
	CONSTRAINT students_courses_relation_course_id_fkey FOREIGN KEY (course_id)
        REFERENCES public.courses (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT students_courses_relation_student_id_fkey FOREIGN KEY (student_id)
        REFERENCES public.students (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);
ALTER TABLE public.students_courses_relation
    OWNER to test_user;