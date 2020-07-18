# Calorie app
An API to keep track of daily calories consumed by user. Also users can set their daily maximum calorie consumption limit. Once this limit exceeds, every food-item consumed thereafter shall have a boolean field set to True for calories_exceeded field.

## Local Setup
```
$ git clone https://github.com/suvhotta/calorie_app_DRF.git
$ cd calorie-tracker-django-restframework
$ pipenv install
$ pipenv shell
$ python manage.py makemigrations
$ python manage.py migrate
```
## Run
```
$ python manage.py runserver
```
## Defining Roles
- <strong>Admin :</strong> Can add/fetch/remove both users and food-items.
- <strong>User Manager :</strong> Can add/fetch/remove only users.
- <strong>Normal User :</strong> Can add/fetch/remove self added food-items.

## Creating admin
To create an admin with default username: admin, password: admin, and max_calories: 2000 <br/>
```
$ python manage.py create_admin
```

To specify the username, password or max_calories: <br/>
```
$ python manage.py create_admin --username <username>
  --password <password> --max_calories <max_calories>
```
The admin account can be therafter used to create more users.
<em> <strong> There isn't any limitation on username and password, however the max_calories should be an integer. </strong> </em>  <br/>

## Structure

In a RESTful API, endpoints (URLs) define the structure of the API and how end users access data from our application using the HTTP methods - GET, POST, PATCH, PUT, DELETE.

| Endpoint    | HTTP Method |  CRUD | RESULT                |
| ----------- | ----------- | ------|--------               |
| register    | POST        | CREATE | creates new user     |
| users       | GET         | READ   | list of all users    |
| users/pk  | GET         | READ   | Single User info     |
| users/pk  | PUT         | UPDATE | Updates a user       |
| users/pk  | PATCH       | UPDATE | Updates a user       |
| users/pk  | DELETE      | DELETE | Deletes a user       |
| fooditem  | POST      | CREATE | Creates a food entry   |
| fooditem  | GET      | READ | List of all fooditems   |
| fooditem/pk  | GET      | READ | Details about a particular food entry  |
| fooditem/pk  | PUT      | UPDATE | Updates a food entry   |
| fooditem/pk  | PATCH      | UPDATE | Updates a food entry   |
| fooditem/pk  | DELETE      | DELETE |Deletes a food entry   |
| login  | POST      | CREATE | Creates a token for user login   |


## Usage
- <strong>Login:</strong>
![login](https://user-images.githubusercontent.com/16841978/87858206-d0bc0500-c949-11ea-8b6f-6a8687f11bd2.png)
The token key thus generated can be passed to the authentication header while accessing other api end-points.

- <strong>User Registration:</strong>
![register](https://user-images.githubusercontent.com/16841978/87858271-58a20f00-c94a-11ea-9d9a-543d73e4ea25.png)

- <strong>Adding Food-item:</strong>
![fooditem](https://user-images.githubusercontent.com/16841978/87858402-4379b000-c94b-11ea-9050-622b33ee1343.png)

- <strong>Filters:</strong>
![filters](https://user-images.githubusercontent.com/16841978/87858411-53918f80-c94b-11ea-9427-9d7043284f9c.png)
