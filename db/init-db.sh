#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER leshka WITH PASSWORD 'leshka';
    CREATE DATABASE mail_drive;

    GRANT ALL PRIVILEGES ON DATABASE mail_drive TO leshka;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO leshka;

EOSQL

PGPASSWORD=leshka psql -v ON_ERROR_STOP=1 --dbname=mail_drive --username=leshka <<-EOSQL
    CREATE TABLE maildrive_user (
        name VARCHAR(256),
        subname VARCHAR(256),
        age INTEGER CHECK (age > 0),
        country VARCHAR(256),
        telephone_number VARCHAR(32),
        email VARCHAR(254) PRIMARY KEY,
        password VARCHAR(256),
        avatar_url VARCHAR(256),
        avatar_token VARCHAR(256)
    );

    CREATE TABLE maildrive_mail (
        id SERIAL PRIMARY KEY,
        header VARCHAR(256),
        content VARCHAR(10240),
        sender_id VARCHAR(256),
        recipient_id VARCHAR(256)
    );

    CREATE TABLE maildrive_mail_data (
        id SERIAL PRIMARY KEY,
        data_url VARCHAR(256),
        data_token VARCHAR(256),
        mail_id integer REFERENCES maildrive_mail (id)
    );

    CREATE TABLE maildrive_mailgroup (
        id SERIAL PRIMARY KEY,
        name VARCHAR(256)
    );

    CREATE TABLE maildrive_user_mail (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(256) REFERENCES maildrive_user (email),
        mail_id integer REFERENCES maildrive_mail (id),
        mailgroup_id integer REFERENCES maildrive_mailgroup (id)
    );

    CREATE TABLE maildrive_log (
        id SERIAL PRIMARY KEY,
        entity VARCHAR(256),
        method VARCHAR(256),
        timestamp timestamp
    );

    INSERT INTO maildrive_user (email, password)
        VALUES
            ('superadmin', 'superadmin');

    INSERT INTO maildrive_mailgroup (id, name)
        VALUES
            (1, 'Incoming'),
            (2, 'Outgoing'),
            (3, 'Drafts');

    BEGIN;
    LOCK TABLE maildrive_mailgroup IN EXCLUSIVE MODE;
    SELECT setval('maildrive_mailgroup_id_seq', COALESCE((SELECT MAX(id)+1 FROM maildrive_mailgroup), 1), false);
    COMMIT;
EOSQL