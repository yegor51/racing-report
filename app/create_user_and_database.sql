CREATE USER test_user WITH PASSWORD '1234';

CREATE DATABASE test_db
    WITH
    OWNER = test_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'Russian_Ukraine.1251'
    LC_CTYPE = 'Russian_Ukraine.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;