drop table if exists entries;
create table entries(
	id integer primary key autoincrement,
	long_url string not null,
	short_url string not null
);