create table if not exists transactions (
    t_id serial primary key,
    t_u_ref integer not null,
    t_name varchar not null,
    t_g_ref integer not null,
    t_amount numeric(10,2) not null,
    t_date date default current_date,
    t_created_at timestamp not null default now()
);