create table if not exists payments (
    p_id serial primary key,
    p_u_sender integer not null,
    p_u_recipient integer not null,
    p_g_ref integer not null,
    p_amount decimal(10,2) not null,
    p_date date default current_date,
    p_created_at timestamp not null default now()
);