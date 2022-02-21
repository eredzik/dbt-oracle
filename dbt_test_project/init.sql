create user dbt_test identified by dbt_test;
grant create session to dbt_test;
grant unlimited tablespace to dbt_test;
grant create table to dbt_test;
grant create view to dbt_test;
alter user dbt_test quota unlimited on USERS;
@ ?/demo/schema/human_resources/hr_main.sql 
GRANT ALL ON HR.REGIONS TO dbt_test;
GRANT ALL ON HR.LOCATIONS TO dbt_test;
GRANT ALL ON HR.DEPARTMENTS TO dbt_test;
GRANT ALL ON HR.JOBS TO dbt_test;
GRANT ALL ON HR.EMPLOYEES TO dbt_test;
GRANT ALL ON HR.JOB_HISTORY TO dbt_test;
GRANT ALL ON HR.COUNTRIES TO dbt_test;
create user dbt_test_out identified by dbt_test_out;
alter user dbt_test_out quota unlimited on USERS;
grant create any table,
    create any view to dbt_test;
create table dbt_test_out.abc as
select 1 as a
from dual;
-- grant select any table,
--     insert any table,
--     delete any table,
--     update any table,
--     drop any table to dbt_test;
grant ALL PRIVILEGES to dbt_test;
grant ALL PRIVILEGES to dbt_test_out;
create or replace force view dbt_test_out.person__dbt_tmp1 as
select *
from hr.employees;