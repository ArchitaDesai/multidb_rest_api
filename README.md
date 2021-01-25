# Multi DB REST API
    A multi DB REST API that fetches data on-the-fly from given database & table, having
    dynamic aggregation & groupby queries' support, built with Django REST framework.


## Features
- Connect to Database dynamically & fetch table data
- Fetch & display all the rows & columns from the given table
- Filter columns to query specific column data in the API
- Filter data with complex queries like group-by & aggregation
- Apply aggregation functions like sum, avg, count, min, max on columns


## For Developers

### Installation Instructions
Run following commands inside the cloned repository:
```
virtualenv -p python3.7 venv
source venv/bin/activate
pip install -r requirements.txt

# To run server
cd multidb_rest_api && python manage.py runserver

# Note: Have included db1.sqlite3 & db2.sqlite3 in this project for sample data
```

### Tech Stack
- Python
- Django
- Django REST framework

### API Endpoint `/api`

#### 1. Query & Fetch Table's data

**Endpoint:** `/api/`

**Method:** POST

**Input Data:**
```
{
	"database_name": "database2",
	"data": {
		"table_name": "User"
	}
}
```

**Response:**
```
{
    "column": [
        "id",
        "first_name",
        "last_name",
        "email",
        "age",
        "city"
    ],
    "data": [
        [
            1,
            "Joey",
            "Tribbiani",
            "joeydb2@gmail.com",
            29,
            "New York City"
        ],
        [
            2,
            "Chandler",
            "Bing",
            "chandlerdb2@gmail.com",
            31,
            "San Diego"
        ],
        ...
    ],
    "length": 2
}
```

#### 2. Filter by Columns & Select required fields

**Endpoint:** `/api/`

**Method:** POST

**Input Data:**
```
{
	"database_name": "database1",
	"data": {
		"select_list": [
			{ "column": "first_name" },
			{ "column": "last_name" }
		],
		"worksheet_id": "user"
	}
}
```

**Response:**
```
{
    "column": [
        "first_name",
        "last_name"
    ],
    "data": [
        [
            "Joey",
            "Tribbiani"
        ],
        [
            "Chandler",
            "Bing"
        ],
        ...
    ],
    "length": 2
}
```

#### 3. Aggregate & Group by query support

**Endpoint:** `/api/`

**Method:** POST

**Example:** Query employee table to show sum of salary & average of years of experience, group by city.

**Input Data:**
```
{
	"database_name": "database1",
	"data": {
		"aggregate": [
			{
				"column": "salary",
				"type": "sum"
			},
			{
				"column": "experience_years",
				"type": "average"
			}
		],
		"groupby": [
			{
				"column": "city"
			}
		],
		"worksheet_id": "employee"
	}
}
```

**Response:**
```
{
    "column": [
        "city",
        "sum_of_salary",
        "average_of_experience_years"
    ],
    "data": [
        [
            "Chicago",
            165000,
            6.5
        ],
        [
            "New York",
            345000,
            7.5
        ]
    ],
    "length": 2
}
```

#### Notes:

1. To apply aggregation functions, use `sum`, `average`, `count`, `min`, `max` as `data.aggregate.type` in the input data
2. To migrate to a specific database (example: `database1`) run following command:
    ```
        python manage.py migrate --database=database1
    ```