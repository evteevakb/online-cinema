# Auth service

The `auth` service is responsible for handling user authentication and authorization. It includes features such as user login, registration, and token management.

## Service structure

- `src`: contains the main application code;
- `tests`: contains tests for the service.

## Installation and testing

For installation and testing see [deploy documentation](../../deploy/auth/README.md).

## Creating superuser

Commands to create superuser:
    
    docker exec -it auth bash
    python3 create_superuser.py admin@test.com 1234

## Service schema

[Schema](https://miro.com/welcomeonboard/R0F6RmtPWVFlNUJ2eitsVHRCMTZ2YVN0SHp3ay9TWCtIR2JEOW5Pelo0cEFRUUFjZklWKy96dTBZL0I0UG5rVDVzOEhQZlVrelpyZEcveDUxUklSc0V0Vno0SnVNRDdKNTdUTWVhZXlHSUtXQ1FaYXNpUzJSVU9OeDdyWDFhOEJBS2NFMDFkcUNFSnM0d3FEN050ekl3PT0hdjE=?share_link_id=611276372820)

## Contributors

- [@Escros1](https://github.com/Escros1)
- [@evteevakb](https://github.com/evteevakb)
- [@IstyxI](https://github.com/IstyxI)
- [@wegas66](https://github.com/wegas66)
