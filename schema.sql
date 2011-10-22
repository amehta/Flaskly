drop table if exists urls;
create table urls (
  id integer primary key autoincrement,
  url_long string not null,
  url_short string not null
);

