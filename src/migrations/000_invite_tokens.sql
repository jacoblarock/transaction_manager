create table invite_tokens (
    it_id serial primary key,
    it_token varchar not null,
    it_expires timestamp not null default (current_timestamp + interval '30 minutes')
);