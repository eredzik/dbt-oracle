create user dbt_test identified by dbt_test;
grant create session to dbt_test;
grant unlimited tablespace to dbt_test;
grant create table to dbt_test;
grant create view to dbt_test;
@ ? / demo / schema / human_resources / hr_main.sql
GRANT ALL ON HR.REGIONS TO dbt_test;
GRANT ALL ON HR.LOCATIONS TO dbt_test;
GRANT ALL ON HR.DEPARTMENTS TO dbt_test;
GRANT ALL ON HR.JOBS TO dbt_test;
GRANT ALL ON HR.EMPLOYEES TO dbt_test;
GRANT ALL ON HR.JOB_HISTORY TO dbt_test;
GRANT ALL ON HR.COUNTRIES TO dbt_test;