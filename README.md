# Calorie app
An API to keep track of daily calories consumed by user. Also users can set their daily maximum calorie consumption limit. Once this limit exceeds, every food-item consumed thereafter shall have a boolean field set to True for calories_exceeded field.

## Local Setup
```
$ git clone https://github.com/suvhotta/calorie_app_DRF.git
$ cd calorie_app_DRF
$ pipenv install
$ pipenv shell
```
- [x] Setup 
## Creating admin
To create an admin with default username: admin, password: admin, and max_calories: 2000 <br/>
```
$ python manage.py create_admin
```

To specify the username, password or max_calories: <br/>
```
$ python manage.py create_admin --username <username> --password <password> --max_calories <max_calories>
```
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


 

