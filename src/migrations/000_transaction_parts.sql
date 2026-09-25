create table if not exists transaction_parts (
    tp_id serial primary key,
    tp_t_ref integer not null,
    tp_u_ref integer not null,
    tp_amount numeric(10,2) not null,
    tp_created_at timestamp not null default now()
);