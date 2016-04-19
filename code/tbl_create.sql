-- create database if not exists eecs564 ;
-- use eecs564;
drop table if exists Data;
create table Data(
	id integer primary key auto_increment,
	state VARCHAR(2) not null,
	gender VARCHAR(1) not null,
	year integer(4) not null,
	name VARCHAR(32) not null,
	occurence integer(24) not null
);
drop table if exists Name;
create table Name(
	nameid integer primary key auto_increment,
	gender VARCHAR(1) not null,
	name VARCHAR(32) not null,
	occurence integer(24) not null,
	beginyear integer(4) not null,
	endyear integer(4) not null,
	p_est DOUBLE not null default -1,
	var DOUBLE not null default -1
);
drop table if exists NameInfo;
create table NameInfo(
	id integer primary key auto_increment,
	gender VARCHAR(1) not null,
	year integer(4) not null,
	name VARCHAR(32) not null,
	occurence integer(24) not null
);