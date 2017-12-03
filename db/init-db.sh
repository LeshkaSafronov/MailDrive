#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER leshka WITH PASSWORD 'leshka';
    CREATE DATABASE mail_drive;

    GRANT ALL PRIVILEGES ON DATABASE mail_drive TO leshka;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO leshka;

EOSQL

PGPASSWORD=leshka psql -v ON_ERROR_STOP=1 --dbname=mail_drive --username=leshka <<-EOSQL
    CREATE TABLE mail_user (
        id SERIAL PRIMARY KEY,
        name VARCHAR(256),
        subname VARCHAR(256),
        age INTEGER CHECK (age > 0),
        country VARCHAR(256),
        telephone_number VARCHAR(32),
        email VARCHAR(254),
        password VARCHAR(256),
        avatar_url VARCHAR(256),
        avatar_token VARCHAR(256)
    );

    CREATE TABLE mail_mail (
        id SERIAL PRIMARY KEY,
        header VARCHAR(256),
        content VARCHAR(256),
        sender_id integer REFERENCES mail_user (id),
        recipient_id integer REFERENCES mail_user (id),
        is_deleted boolean DEFAULT false
    );

    CREATE TABLE mail_mail_data (
        id SERIAL PRIMARY KEY,
        data_url VARCHAR(256),
        data_token VARCHAR(256),
        mail_id integer REFERENCES mail_mail (id)
    );

    INSERT INTO mail_user (email, password)
        VALUES
            ('superadmin', 'superadmin')
EOSQL