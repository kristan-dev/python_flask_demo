CREATE SCHEMA IF NOT EXISTS sample_schema;

create table sample_schema.users (
	user_number serial primary key,
	email text,
	password text,
	username text,
	user_type text
);

create table sample_schema.lists (
	list_number serial primary key,
	title text,
	cards jsonb
);

create table sample_schema.cards (
	card_number serial PRIMARY KEY,
	fk_list_number INT,
	title text,
	description text,
	comments jsonb,
	CONSTRAINT fk_list
      FOREIGN KEY(fk_list_number)
	  REFERENCES sample_schema.lists(list_number)
);

create table comments (
	comment_number serial primary key,
	fk_card_number int,
	CONSTRAINT fk_card
	    FOREIGN KEY (fk_card_number)
	        REFERENCES sample_schema.cards(card_number),
	content text,
	replies jsonb
);