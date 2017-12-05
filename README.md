# MailDrive
API:

USERS:

POST /api/users/singup <br>
Sing up user

REQUEST
```json
{
    "name": "Alexey",
    "subname": "Safronov",
    "age": 20,
    "country": "Mogilev",
    "telephone_number": "222322",
    "email": "diamond.alex97@gmail.com",
    "password": "123"
}
```

RESPONSE
```json
{
    "id": 2,
    "name": "Alexey",
    "subname": "Safronov",
    "age": 20,
    "country": "Mogilev",
    "telephone_number": "222322",
    "email": "diamond.alex97@gmail.com",
    "password": "123",
    "avatar_url": null,
    "avatar_token": null
}
```

GET /api/users <br />
Get all users

RESPONSE
```json
[
    {
        "id": 1,
        "name": null,
        "subname": null,
        "age": null,
        "country": null,
        "telephone_number": null,
        "email": "superadmin",
        "password": "superadmin",
        "avatar_url": null,
        "avatar_token": null
    },
    {
        "id": 2,
        "name": "Alexey",
        "subname": "Safronov",
        "age": 20,
        "country": "Mogilev",
        "telephone_number": "222322",
        "email": "diamond.alex97@gmail.com",
        "password": "123",
        "avatar_url": null,
        "avatar_token": null
    }
]
```
<br>

GET /api/users/:id <br />
Get user with supplied id

RESPONSE
```json
{
    "id": 2,
    "name": "Alexey",
    "subname": "Safronov",
    "age": 20,
    "country": "Mogilev",
    "telephone_number": "222322",
    "email": "diamond.alex97@gmail.com",
    "password": "123",
    "avatar_url": null,
    "avatar_token": null
}
```

POST /api/users <br />
Create user

REQUEST
```json
{
    "name": "Cheburashka",
    "subname": "Gena",
    "age": 28,
    "country": "Mogilev",
    "telephone_number": "3456",
    "email": "gena@cheburashka.com",
    "password": "hello"
}
```
RESPONSE <br />
Status: 201 CREATED
```json
{
    "id": 3,
    "name": "Cheburashka",
    "subname": "Gena",
    "age": 28,
    "country": "Mogilev",
    "telephone_number": "3456",
    "email": "gena@cheburashka.com",
    "password": "hello",
    "avatar_url": null,
    "avatar_token": null
}
```

PUT /api/users/:id <br />
Update user with supplied id <br />
REQUEST
```json
{
    "id": 3,
    "name": "Cheburashka",
    "subname": "Gena",
    "age": 1,
    "country": "Vitebsk"
}
```
RESPONSE <br >
Status: 200 OK
```json
{
    "id": 3,
    "name": "Cheburashka",
    "subname": "Gena",
    "age": 1,
    "country": "Vitebsk",
    "telephone_number": "3456",
    "email": "gena@cheburashka.com",
    "password": "hello",
    "avatar_url": null,
    "avatar_token": null
}
```


DELETE /api/users/:id <br />
Delete user with supplied id <br />
Status: 204 NO CONTENT


PUT /api/users/:id/avatar <br />
Update user avatar <br />
REQUEST

BINARY FILE

RESPONSE <br >
Status: 200 OK
```json
{
    "avatar_url": "/api/users/3/avatar?imghash=5722490373467547207"
}
```


GET /api/users/:id/avatar <br />
RESPONSE <br />
Status: 200 OK

BINARY FILE

Content-length: 3111054
Content-type: image/jpeg


POST /api/users/login <br />
REQUEST <br />

```json
{
   "email": "kek@cheburek.com",
   "password": "kekker_cheburekker"
}
```

RESPONSE <br>
Status: 200 OK


POST /api/users/logout <br />
RESPONSE <br>
Status: 200 OK