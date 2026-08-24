create table if not exists users (
    u_id serial primary key,
    u_name varchar not null,
    u_pass varchar not null,
    u_created_at timestamp not null default now()
);