# Booking System - MySQL Database & Flask Back-End

A university database development project demonstrating relational database design, normalization, REST API development using Python and Flask, MySQL integration, and advanced SQL programming techniques.

The repository contains two laboratory projects based on the same hotel booking management system:

- **Laboratory Work 4 - Back-End Development with Flask + Python and MySQL**
- **Laboratory Work 5 - Stored Programs in MySQL (Stored Procedures, Functions, Triggers and Cursors)**

The project demonstrates how to design a relational database, develop a structured Back-End application, implement CRUD operations, manage relationships between database entities, and create programmable database objects to automate business logic and maintain data integrity.

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technologies](#2-technologies)
3. [Database Description](#3-database-description)
4. [Laboratory Work 4 - Flask Back-End](#4-laboratory-work-4--flask-back-end)
5. [Laboratory Work 5 - Stored Programs in MySQL](#5-laboratory-work-5--stored-programs-in-mysql)
6. [Project Architecture](#6-project-architecture)
7. [Repository Structure](#7-repository-structure)
8. [Installation and Configuration](#8-installation-and-configuration)
9. [Running Laboratory Work 4](#9-running-laboratory-work-4)
10. [Running Laboratory Work 5](#10-running-laboratory-work-5)
11. [API Documentation](#11-api-documentation)
12. [SQL Examples](#13-sql-examples)
13. [Testing](#14-testing)
14. [Learning Outcomes](#15-learning-outcomes)
15. [Conclusion](#16-conclusion)

---

# 1. Project Overview

**Booking System** is a relational database and Back-End application designed to manage hotel reservations and related information.

The system models the main processes of a hotel booking platform, including:

- User registration and management.
- Hotel chain management.
- Storage of hotel locations.
- Hotel information management.
- Room types and room availability.
- Reservation creation and management.
- Email confirmation records.
- Payment hold management.
- Customer reviews and ratings.

The project was developed in two stages.

### Laboratory Work 4 - Back-End Development

The fourth laboratory focuses on developing a Back-End application using Python and Flask, connected to a MySQL relational database.

The main objectives are:

- Reviewing the database structure and implementing the required relationships.
- Implementing CRUD operations for all database tables.
- Separating application logic into controllers, services, DAO and DTO layers.
- Implementing SQL queries for retrieving related data.
- Testing HTTP requests and responses using Postman.

### Laboratory Work 5 - Stored Programs in MySQL

The fifth laboratory extends the existing database by introducing programmable SQL objects.

The main objectives are:

- Creating an additional table with a 1:M relationship maintained by triggers instead of a physical foreign key.
- Implementing parameterized stored procedures.
- Implementing an M:M relationship through an associative table.
- Creating a procedure for inserting ten records with automatically generated names.
- Developing a user-defined function for aggregate calculations.
- Implementing a stored procedure using a cursor.
- Creating triggers for data validation and deletion auditing.
- Integrating stored procedure execution into Flask controllers.

Both laboratory works use the same database, `booking_system`, and represent different stages of development of one application.

---

# 2. Technologies

The project uses the following technologies:

| Technology | Purpose |
|---|---|
| Python 3.10+ | Back-End programming language |
| Flask | Web framework for developing REST API endpoints |
| MySQL 8.0+ | Relational database management system |
| MySQL Connector/Python | Communication between Python and MySQL |
| SQL | Database definition, queries and stored programs |
| Postman | API testing |
| PyCharm | Development environment |
| PyYAML | Application configuration |
| python-dotenv | Environment variable management |
| pytest / unittest | Automated testing |

---

# 3. Database Description

## 3.1. Database

The project uses a MySQL database named:

`booking_system`

The database contains ten main relational tables.

| Table | Description |
|---|---|
| `users` | Stores registered users and their personal information |
| `hotel_chains` | Stores hotel chain information |
| `locations` | Stores countries, cities and postal codes |
| `hotels` | Stores hotel information and references to hotel chains and locations |
| `room_types` | Stores room categories, prices and maximum guest capacity |
| `rooms` | Stores individual hotel rooms and their availability |
| `reservations` | Stores customer bookings, dates, prices and reservation status |
| `email_confirmations` | Stores notification and email confirmation records |
| `payment_holds` | Stores payment hold information and payment statuses |
| `reviews` | Stores customer reviews and hotel ratings |

## 3.2. Primary and Foreign Keys

Each main table has a surrogate primary key implemented using `BIGINT AUTO_INCREMENT`.

Primary keys provide unique identification of records.

Foreign keys are used to maintain relationships between related tables.

Examples:

- `hotels.chain_id` references `hotel_chains.chain_id`.
- `hotels.location_id` references `locations.location_id`.
- `room_types.hotel_id` references `hotels.hotel_id`.
- `rooms.room_type_id` references `room_types.room_type_id`.
- `reservations.user_id` references `users.user_id`.
- `reservations.room_id` references `rooms.room_id`.
- `reviews.user_id` references `users.user_id`.
- `reviews.hotel_id` references `hotels.hotel_id`.

## 3.3. Database Relationships

The database implements the following relationships:

**One-to-Many (1:M):**

- One hotel chain can contain multiple hotels.
- One location can contain multiple hotels.
- One hotel can have multiple room types.
- One hotel can contain multiple rooms.
- One user can have multiple reservations.
- One room can appear in multiple reservations over time.

**Many-to-Many (M:M):**

The M:M relationship between `users` and `hotels` is implemented through the associative table `reviews`.

One user can review multiple hotels, and one hotel can receive reviews from multiple users.

The associative table stores additional relationship attributes, including rating, comment and review date.

---

# 4. Laboratory Work 4 - Flask Back-End

## 4.1. Objective

The objective of Laboratory Work 4 is to implement a Back-End application using Flask and Python with a MySQL database connection.

The application provides a REST API for interacting with the database and supports standard CRUD operations.

The implementation follows a layered architecture to separate HTTP request handling, business logic, database access and data transfer.

## 4.2. Application Architecture

The Back-End is divided into several logical layers.

### Controller Layer

Location:

`app/my_project/auth/controller/booking_controller.py`

Controllers receive HTTP requests from clients, process request parameters, call the appropriate service methods and return JSON responses.

Controllers are responsible for communication between the API and the application logic.

### Service Layer

Location:

`app/my_project/service/booking_service.py`

The service layer contains business logic and input validation.

It checks required fields, validates dates, email addresses, ratings and other values before passing operations to the database layer.

### DAO Layer

DAO stands for Data Access Object.

Files:

- `app/my_project/dao/base_dao.py`
- `app/my_project/dao/relationship_dao.py`

The DAO layer provides methods for communicating with MySQL.

`base_dao.py` implements generic database access operations, while `relationship_dao.py` contains queries for retrieving related entities using SQL JOIN operations.

Parameterized queries are used for passing user-supplied values to SQL statements.

### DTO and Schema Layer

Location:

- `app/my_project/domain/dto.py`
- `app/my_project/domain/schemas.py`

DTO stands for Data Transfer Object.

DTO objects define the structure of data returned by the API.

Schemas define supported fields and validation rules for database entities.

### Database Connection

Location:

`app/my_project/utils/db.py`

This module handles MySQL connection management and provides the database connection used by DAO components.

## 4.3. CRUD Operations

CRUD represents four basic database operations:

| Operation | HTTP Method | Description |
|---|---|---|
| Create | POST | Inserts a new record |
| Read | GET | Retrieves records |
| Update | PUT / PATCH | Modifies existing records |
| Delete | DELETE | Deletes a record |

CRUD functionality is implemented for all ten main database resources:

`users`, `hotel_chains`, `locations`, `hotels`, `room_types`, `rooms`, `reservations`, `email_confirmations`, `payment_holds`, `reviews`.

The API supports:

- Retrieving all records with pagination using `limit` and `offset`.
- Retrieving an individual record by its ID.
- Creating new records.
- Updating existing records.
- Deleting records.

Primary key values are generated automatically by MySQL using `AUTO_INCREMENT`.

## 4.4. Relationship Queries

The application also implements SQL JOIN queries for retrieving data from related tables.

Examples:

| Endpoint | Description |
|---|---|
| `GET /api/hotels/with-location` | Retrieves hotels with their locations and hotel chains |
| `GET /api/locations/1/hotels` | Retrieves all hotels belonging to a specific location |
| `GET /api/reservations/details` | Retrieves reservation information with related users, rooms, hotels and locations |
| `GET /api/hotels/1/reviewers` | Retrieves users who reviewed a particular hotel |
| `GET /api/users/1/reviewed-hotels` | Retrieves hotels reviewed by a particular user |

These queries demonstrate 1:M, M:1 and M:M relationships.

## 4.5. Additional Indexes

Two additional indexes were implemented to improve query performance:

- `idx_reservation_dates` - composite index on `reservations(check_in_date, check_out_date)`, designed to support date-based reservation searches.
- `idx_user_email` - unique index on `users(email)`, providing efficient email lookups and preventing duplicate email addresses.

---

# 5. Laboratory Work 5 - Stored Programs in MySQL

## 5.1. Objective

The objective of Laboratory Work 5 is to extend the existing `booking_system` database by implementing stored procedures, a user-defined function, triggers and a cursor.

These database objects allow business logic and data integrity rules to be implemented directly inside MySQL.

The laboratory also extends the existing Flask Back-End by providing API endpoints for executing stored procedures.

## 5.2. Additional Table and 1:M Relationship Without a Physical Foreign Key

An additional table named `hotel_notes` was created.

It stores notes associated with hotels.

The table structure contains:

| Column | Description |
|---|---|
| `note_id` | Primary key |
| `hotel_id` | Identifier of the related hotel |
| `title` | Note title |
| `note_text` | Note content |
| `created_at` | Creation timestamp |

The table has a logical 1:M relationship with the existing `hotels` table.

One hotel may contain multiple notes.

Unlike a conventional foreign key relationship, the `hotel_id` column does not have a physical FOREIGN KEY constraint.

Instead, referential integrity is maintained using MySQL triggers.

### Triggers for Referential Integrity

| Trigger | Event | Purpose |
|---|---|---|
| `bi_hotel_notes_validate_hotel` | BEFORE INSERT | Checks whether the referenced hotel exists |
| `bu_hotel_notes_validate_hotel` | BEFORE UPDATE | Validates the hotel reference when a note is updated |
| `ad_hotels_remove_notes` | AFTER DELETE | Removes associated notes when a hotel is deleted |
| `bu_hotels_protect_note_parent_id` | BEFORE UPDATE | Prevents changing a hotel ID while notes reference it |

The validation triggers use `SIGNAL SQLSTATE '45000'` to reject invalid operations.

This demonstrates how trigger-based validation can replace the basic referential checks normally provided by a physical foreign key.

## 5.3. Stored Procedure for Parameterized Insertion

Procedure:

`sp_add_hotel_note`

Purpose: to insert a new record into `hotel_notes` using input parameters.

Parameters:

- `p_hotel_id`
- `p_title`
- `p_note_text`

The procedure validates required text fields and inserts a new note.

The referenced hotel is validated by the `BEFORE INSERT` trigger.

Example:

```sql
CALL sp_add_hotel_note(
    1,
    'Reception',
    'Late check-in possible'
);
```

This procedure demonstrates parameterized data insertion using a stored MySQL procedure.

## 5.4. Stored Procedure for Many-to-Many Relationship

Procedure:

`sp_add_review_by_names`

Purpose: to create a new M:M relationship between a user and a hotel through the existing associative table `reviews`.

The procedure accepts:

- User first name.
- User last name.
- Hotel name.
- Rating.
- Comment.
- Review date.

The procedure performs the following operations:

1. Searches for the user using their first and last name.
2. Checks that exactly one matching user exists.
3. Searches for the hotel using its name.
4. Checks that exactly one matching hotel exists.
5. Obtains the corresponding primary key values.
6. Inserts a new record into `reviews`.

The procedure also validates the rating range from 1 to 5.

Example:

```sql
CALL sp_add_review_by_names(
    'Іван',
    'Петренко',
    'Hilton Kyiv',
    5,
    'Excellent hotel',
    CURRENT_DATE
);
```

This demonstrates how an associative table can be populated using real existing entities rather than manually supplied foreign key values.

## 5.5. Procedure for Inserting Ten Noname Records

Procedure:

`sp_insert_ten_noname`

Purpose: to automatically insert ten records into `hotel_chains` using names generated according to the `NonameN` format.

The procedure receives one input parameter:

`p_start_number`

It then executes a `WHILE` loop that inserts ten records.

Example:

```sql
CALL sp_insert_ten_noname(500);
```

Generated names:

```text
Noname500
Noname501
Noname502
Noname503
Noname504
Noname505
Noname506
Noname507
Noname508
Noname509
```

The procedure uses the SQL `CONCAT()` function to generate names dynamically.

**Note:** MySQL does not provide Oracle-style stored PACKAGE containers. Therefore, the requested package-like functionality is implemented as a reusable stored procedure.

## 5.6. User-Defined Function for Aggregate Calculations

Function:

`fn_reservation_metric`

Purpose: to calculate an aggregate value for the `reservations.total_price` column.

The function supports four aggregate operations:

| Operation | Description |
|---|---|
| `MAX` | Returns the maximum reservation price |
| `MIN` | Returns the minimum reservation price |
| `SUM` | Returns the sum of reservation prices |
| `AVG` | Returns the average reservation price |

Example:

```sql
SELECT fn_reservation_metric('AVG');
```

The function uses a `CASE` statement to select the appropriate aggregate calculation.

### Stored Procedure Calling the Function

Procedure:

`sp_show_reservation_metric`

This procedure validates the requested operation and executes the user-defined function inside a SELECT statement.

Example:

```sql
CALL sp_show_reservation_metric('AVG');
```

The procedure returns the requested operation, calculated value and source column.

This demonstrates the integration of a user-defined function with a stored procedure.

## 5.7. Cursor Procedure - Dynamic Table Creation and Random Data Distribution

Procedure:

`sp_split_users_with_cursor`

This procedure implements the first cursor-based option from the laboratory requirements.

The objective is to create two new tables with timestamp-based names and distribute records from the original `users` table between them randomly.

### How the Cursor Works

The procedure performs the following steps:

1. Declares a cursor for reading records from `users`.
2. Declares variables for storing the current user's fields.
3. Creates two table names containing a timestamp.
4. Dynamically creates two tables using `CREATE TABLE ... LIKE users`.
5. Opens the cursor.
6. Reads records one by one using `FETCH`.
7. Generates a random value using `RAND()`.
8. Inserts the current record into either the first or the second table.
9. Continues until all source records have been processed.
10. Closes the cursor and releases prepared SQL statements.
11. Returns the names of the created tables.

### Important Cursor Commands

| SQL command | Purpose |
|---|---|
| `DECLARE CURSOR` | Declares the cursor and its SELECT query |
| `OPEN` | Opens the cursor |
| `FETCH` | Reads the next record |
| `LOOP` | Repeats record processing |
| `CONTINUE HANDLER` | Handles the end of the result set |
| `RAND()` | Generates a random distribution decision |
| `LEAVE` | Exits the loop |
| `CLOSE` | Closes the cursor |

The generated tables have names similar to:

```text
users_split_a_20261021131500123456
users_split_b_20261021131500123456
```

Each execution generates new table names.

The original `users` table remains unchanged.

The number of records in each generated table is random, but all source records should be copied into exactly one of the two destination tables.

Example invocation:

```sql
CALL sp_split_users_with_cursor(
    @table_a,
    @table_b
);

SELECT @table_a, @table_b;
```

This demonstrates cursor-based row processing and dynamic SQL execution.

## 5.8. Additional Triggers for Reservation Validation and Auditing

Three additional triggers were implemented for the existing `reservations` table.

### Trigger 1 - BEFORE INSERT

Name:

`bi_reservations_validate_dates_price`

Purpose:

Validates new reservation records before insertion.

It checks that:

- The checkout date is later than the check-in date.
- The total reservation price is greater than zero.

Invalid records are rejected using `SIGNAL SQLSTATE '45000'`.

### Trigger 2 - BEFORE UPDATE

Name:

`bu_reservations_validate_dates_price`

Purpose:

Applies the same validation rules when an existing reservation is updated.

This ensures that invalid reservation data cannot be introduced through update operations.

### Trigger 3 - AFTER DELETE

Name:

`ad_reservations_write_delete_log`

Purpose:

Automatically stores information about deleted reservations in the audit table `reservation_delete_log`.

The log stores:

- Deleted reservation ID.
- User ID.
- Room ID.
- Check-in date.
- Check-out date.
- Total price.
- Reservation status.
- Deletion timestamp.

This demonstrates automatic audit logging using an AFTER DELETE trigger.

### Audit Table

`reservation_delete_log`

The table preserves information about deleted reservations for auditing and historical tracking.

This allows the application to retain deletion information even after the original reservation record has been removed.

## 5.9. Total Number of Database Triggers

The SQL script creates seven triggers in total:

| Group | Number | Purpose |
|---|---:|---|
| `hotel_notes` and `hotels` integrity | 4 | Trigger-based 1:M integrity |
| `reservations` validation and auditing | 3 | Data validation and deletion logging |
| **Total** | **7** | |

---

# 6. Project Architecture

Both laboratory projects use a layered Back-End architecture.

The overall request processing flow is:

```text
                 Postman Client
                       |
                       v
                Flask Controller
                       |
                       v
                  Service Layer
                       |
                       v
                    DAO Layer
                       |
                       v
                  MySQL Database
                       |
             +---------+---------+
             |                   |
             v                   v
       Stored Procedures       Triggers
             |
             v
       SQL Results
             |
             v
          JSON DTO
             |
             v
          Postman
```

### Controller

Receives HTTP requests and returns HTTP responses.

### Service

Contains application-level validation and business logic.

### DAO

Provides database access and executes SQL queries and stored procedures.

### DTO

Defines the structure of data transferred between the Back-End and the client.

### MySQL

Stores data and executes database-side logic, including triggers, functions, stored procedures and cursor operations.

---

# 7. Repository Structure

The repository contains two independent laboratory project directories.

```text
databases-labs/
│
├── README.md
├── .gitignore
│
├── lab4/
│   │
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── data.sql
│   ├── postman_collection.json
│   │
│   └── app/
│       ├── config/
│       │   └── app.yml
│       │
│       └── my_project/
│           ├── auth/
│           │   └── controller/
│           │       └── booking_controller.py
│           │
│           ├── service/
│           │   └── booking_service.py
│           │
│           ├── dao/
│           │   ├── base_dao.py
│           │   └── relationship_dao.py
│           │
│           ├── domain/
│           │   ├── dto.py
│           │   └── schemas.py
│           │
│           ├── route/
│           │   └── api_routes.py
│           │
│           └── utils/
│               └── db.py
│
└── lab5/
    │
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    ├── postman_collection.json
    │
    ├── app/
    │   ├── config/
    │   │   └── app.yml
    │   │
    │   └── my_project/
    │       ├── factory.py
    │       │
    │       ├── controller/
    │       │   └── stored_programs_controller.py
    │       │
    │       ├── service/
    │       │   └── stored_programs_service.py
    │       │
    │       ├── dao/
    │       │   └── stored_programs_dao.py
    │       │
    │       └── dto/
    │           └── responses.py
    │
    ├── sql/
    │   ├── base_schema_and_data.sql
    │   └── stored_programs.sql
    │
    └── tests/
        └── test_service.py
```

*The two Flask applications are maintained separately to preserve the independent structure of the laboratory assignments. File paths can be adjusted to match the final uploaded repository.*

---

# 8. Installation and Configuration

## 8.1. Requirements

Before running the projects, install:

- Python 3.10 or newer.
- MySQL Server 8.0 or newer.
- MySQL Workbench (recommended).
- PyCharm or another Python IDE.
- Postman.

## 8.2. Clone the Repository

```bash
git clone https://github.com/binaryframe/databases-labs.git

cd databases-labs
```

## 8.3. Create the Database

For a fresh installation, use the SQL script from Laboratory Work 4:

```bash
cd lab4

mysql -u root -p < data.sql
```

This script creates the `booking_system` database, its ten main tables, relationships, indexes and test data.

**Warning:** The Laboratory Work 4 `data.sql` script drops and recreates the main tables. Running it again can delete existing application data.

If the database already exists and contains the required data, do not rerun this script.

## 8.4. Configure Laboratory Work 4

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file based on `.env.example`.

Configure:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=booking_system
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
```

The application also uses configuration from `app/config/app.yml`.

## 8.5. Configure Laboratory Work 5

Open the `lab5` directory:

```bash
cd ../lab5
```

Create and activate a separate virtual environment, then install dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example`.

Configure:

```env
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=1

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=booking_system
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
```

Use your actual MySQL credentials.

---

# 9. Running Laboratory Work 4

Make sure the MySQL Server is running.

Open a terminal in the `lab4` directory and execute:

```bash
python app.py
```

The Flask application should start at:

```text
http://127.0.0.1:5000
```

The REST API base URL is:

```text
http://127.0.0.1:5000/api
```

Health check:

```http
GET /api/health
```

The API can now be tested using Postman.

---

# 10. Running Laboratory Work 5

Laboratory Work 5 extends the existing `booking_system` database.

**Important:** Run the following SQL script only after the Laboratory Work 4 database has been created.

From the `lab5` directory, execute:

```bash
mysql -u root -p < sql/stored_programs.sql
```

This script creates:

- `hotel_notes`;
- `reservation_delete_log`;
- Seven triggers;
- Five stored procedures;
- One user-defined function.

The script does not recreate or delete the original ten database tables.

Start the Flask application:

```bash
python app.py
```

The application is available at:

```text
http://127.0.0.1:5000
```

Both laboratory applications use port `5000` by default. Run them separately, or configure different ports if you need to run them simultaneously.

---

# 11. API Documentation

## Laboratory Work 4 - CRUD API

Base URL:

`http://127.0.0.1:5000/api`

Generic CRUD endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/<resource>` | Retrieve all records |
| POST | `/api/<resource>` | Create a record |
| GET | `/api/<resource>/<id>` | Retrieve one record |
| PUT/PATCH | `/api/<resource>/<id>` | Update a record |
| DELETE | `/api/<resource>/<id>` | Delete a record |

Available resources:

```text
users
hotel_chains
locations
hotels
room_types
rooms
reservations
email_confirmations
payment_holds
reviews
```

Example:

```http
POST /api/users
Content-Type: application/json
```

```json
{
  "first_name": "Test",
  "last_name": "User",
  "email": "test.user@example.com",
  "phone_number": "+380501112233",
  "registration_date": "2026-10-13"
}
```

## Laboratory Work 5 - Stored Procedure Endpoints

Base URL:

`http://127.0.0.1:5000/api`

| Method | Endpoint | Database Object |
|---|---|---|
| POST | `/procedures/hotel-notes` | `sp_add_hotel_note` |
| POST | `/procedures/reviews-by-names` | `sp_add_review_by_names` |
| POST | `/procedures/noname-chains` | `sp_insert_ten_noname` |
| GET | `/procedures/reservation-metric?operation=AVG` | `sp_show_reservation_metric` and `fn_reservation_metric` |
| POST | `/procedures/split-users` | `sp_split_users_with_cursor` |

Additional endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/hotels/1/notes` | Retrieve hotel notes |
| PATCH | `/hotel-notes/1` | Update a hotel note |
| POST | `/reservations` | Create a reservation |
| DELETE | `/reservations/11` | Delete a reservation |
| GET | `/audit/reservation-deletions?limit=100` | Retrieve deletion audit log |

The reservation ID used in the DELETE request must correspond to an existing test reservation.

---

# 12. SQL Examples

The following examples can be executed directly in MySQL Workbench.

Select the database:

```sql
USE booking_system;
```

### Retrieve all users

```sql
SELECT *
FROM users;
```

### Retrieve hotels with locations

```sql
SELECT
    h.name AS hotel_name,
    l.country,
    l.city
FROM hotels h
JOIN locations l
    ON h.location_id = l.location_id;
```

### Insert a hotel note using a stored procedure

```sql
CALL sp_add_hotel_note(
    1,
    'Reception',
    'Late check-in possible'
);
```

### Create a review using real names

```sql
CALL sp_add_review_by_names(
    'Іван',
    'Петренко',
    'Hilton Kyiv',
    5,
    'Excellent hotel',
    CURRENT_DATE
);
```

### Generate ten Noname records

```sql
CALL sp_insert_ten_noname(500);
```

### Calculate the average reservation price

```sql
CALL sp_show_reservation_metric('AVG');
```

### Calculate the maximum reservation price

```sql
CALL sp_show_reservation_metric('MAX');
```

### Execute the cursor procedure

```sql
CALL sp_split_users_with_cursor(
    @table_a,
    @table_b
);

SELECT @table_a, @table_b;
```

### Retrieve deleted reservation logs

```sql
SELECT *
FROM reservation_delete_log
ORDER BY deleted_at DESC;
```

---

# 13. Testing

Both projects include automated tests for their respective Python application layers.

### Laboratory Work 4

Run the unit tests from the `lab4` directory:

```bash
python -m unittest discover -s app/tests -v
```

The tests cover DTO structures, CRUD business logic and validation.

### Laboratory Work 5

Run the unit tests from the `lab5` directory:

```bash
pytest -q
```

The tests cover service-layer validation and application logic.

Unit tests do not replace integration testing against a real MySQL server.

For complete verification, database procedures, triggers, functions and cursor operations should also be executed against the configured MySQL database and tested through Postman.

---

# 14. Learning Outcomes

The two laboratory works provide practical experience in relational database development and Back-End programming.

The project demonstrates the following skills:

**Database Design**
- Designing relational database schemas.
- Working with primary and foreign keys.
- Applying relational normalization principles.
- Implementing 1:M, M:1 and M:M relationships.
- Creating indexes for improving query performance.

**Python and Back-End Development**
- Developing REST APIs with Flask.
- Organizing application code using layered architecture.
- Working with controllers, services, DAO and DTO.
- Establishing database connections with MySQL Connector/Python.
- Validating HTTP request data.
- Returning structured JSON responses.

**Advanced MySQL Programming**
- Creating and executing stored procedures.
- Developing user-defined SQL functions.
- Implementing database triggers.
- Using cursors to process records sequentially.
- Executing dynamic SQL statements.
- Implementing database audit logging.
- Maintaining data integrity using database-level logic.

**API Testing**
- Testing GET, POST, PUT, PATCH and DELETE requests.
- Testing stored procedure calls through REST API endpoints.
- Checking successful and unsuccessful database operations.
- Verifying database changes using MySQL Workbench and Postman.

---

# 15. Conclusion

This repository demonstrates the development of a hotel booking management system across two stages of database and Back-End development.

Laboratory Work 4 focuses on designing and implementing a Flask-based REST API connected to a MySQL relational database. It provides CRUD operations for ten database tables, implements queries for related entities and demonstrates the use of layered architecture to organize application logic.

Laboratory Work 5 extends the same database with advanced MySQL programming features, including stored procedures, a user-defined function, triggers and a cursor. These database objects automate data insertion, validate business rules, maintain referential integrity and support auditing operations. Their functionality is integrated into the Flask Back-End and can be tested through Postman.

Together, the two projects demonstrate the interaction between a relational database, SQL programming constructs and a Python Back-End application.

---
