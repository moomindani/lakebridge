-- Has to be executed on CDB
-- spool results/config_instance.csv
select inst_id,instance_name,version,database_type from gv$instance

