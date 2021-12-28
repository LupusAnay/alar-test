create table public.users
(
    id       bigserial primary key,
    username text unique not null,
    password bytea       not null,
    is_rw    boolean     not null
);

insert into public.users (username, password, is_rw)
values ('root',
        decode('84dba11ad2bf9d467682bd242b4ed7b5892af336961a1561abffe3f7d2be539adb420c8745c069fda72378ea31e75a20',
               'hex'), true)