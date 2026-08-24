create table if not exists groups (
    g_id serial primary key,
    g_name varchar not null,
    g_created_at timestamp not null default now()
);