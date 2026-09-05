create table sessions (
    s_id serial primary key,
    s_u_ref integer not null,
    s_token varchar not null,
    s_expires timestamp not null default (current_timestamp + interval '30 minutes')
);