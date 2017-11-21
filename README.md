# MailDrive
API:

USERS:

GET /users <br />
Get all users
```json
[
    {
        "id": 37,
        "name": "Alexey",
        "subname": "Gena",
        "age": 28,
        "country": "Minsk",
        "telephone_number": "34573895754",
        "email": "gena@cheburashka.com",
        "password": "hello"
    },
    {
        "id": 38,
        "name": "Leshka",
        "subname": "Safronov",
        "age": 20,
        "country": "Minsk",
        "telephone_number": "11111111111111",
        "email": "gena@alexeyka.com",
        "password": "kek"
    }
]
```


GET /users/:id <br />
Get user with supplied id

RESPONSE
```json
{
    "id": 37,
    "name": "Alexey",
    "subname": "Gena",
    "age": 28,
    "country": "Minsk",
    "telephone_number": "34573895754",
    "email": "gena@cheburashka.com",
    "password": "hello"
}
```

POST /users <br />
Create user

REQUEST
```json
{
    "name": "Cheburashka",
    "subname": "Gena",
    "age": 28,
    "country": "Mogilev",
    "telephone_number": "222322",
    "email": "gena@cheburashka.com",
    "password": "hello"
}
```
RESPONSE <br />
Status: 201 CREATED
```json
{
    "id": 37,
    "name": "Cheburashka",
    "subname": "Gena",
    "age": 28,
    "country": "Mogilev",
    "telephone_number": "222322",
    "email": "gena@cheburashka.com",
    "password": "hello"
}
```

PUT /users/:id <br />
Update user with supplied id <br />
REQUEST
```json
{
    "id": 37,
    "name": "Alexey",
    "subname": "Gena",
    "age": 28,
    "country": "Minsk",
    "telephone_number": "34573895754",
    "email": "gena@cheburashka.com",
    "password": "hello"
}
```
RESPONSE <br >
Status: 200 OK
```json
{
    "id": 37,
    "name": "Alexey",
    "subname": "Gena",
    "age": 28,
    "country": "Minsk",
    "telephone_number": "34573895754",
    "email": "gena@cheburashka.com",
    "password": "hello"
}
```

DELETE /users/:id <br />
Delete user with supplied id <br />
Status: 204 NO CONTENT
