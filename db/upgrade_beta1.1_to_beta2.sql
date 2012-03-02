
-- 2009-12-16: added time when test got queued, this used in the normal urls
alter table test add column queued timestamp without time zone;

update test set queued = started where queued is null or queued = 0;


-- 2009-12-18: goldstar counter added
alter table result add column goldstar integer default 0;
