create table if not exists user_group_map (
    ugm_id serial primary key,
    ugm_u_ref integer not null,
    ugm_g_ref integer not null,
    ugm_created_at timestamp not null default now()
);