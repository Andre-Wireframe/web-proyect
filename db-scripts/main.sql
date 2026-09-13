create database if not exists web_proyect;
use web_proyect;

create table if not exists users (
	id int not null auto_increment primary key,
    name varchar(255) not null unique,
    password varchar(255) not null,
    
    index(name)
);

create table if not exists files (
	id int not null auto_increment primary key,
    name varchar(255) not null unique,
    route varchar(355) not null unique,
    user int not null,
    upload_at datetime default current_timestamp,
    visivility bool default true,
    constraint file_user_fk foreign key(user) references users(id),
    
    index(name)
);

alter table files
add column upload_at datetime default current_timestamp;