begin;

-- Flag for queued tests are waiting for user input
alter table queue add column waiting_input boolean default false;

-- Flag for slow tests in the queue
alter table queue add column slow boolean default false;
alter table test add column slow boolean default false;

-- Time when the test actually finished.
alter table test add column finished timestamp without time zone;

-- Mark old tests as finished
update test set ended = now() where ended is null;
update test set finished = now();

-- Add parent child releations
ALTER TABLE result ADD column parent integer default null;
ALTER TABLE test ADD column parent integer default null;
ALTER TABLE queue ADD column parent integer default null;

commit;
