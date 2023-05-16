# DirectusPyWrapper

DirectusPyWrapper is a Python wrapper for interacting with the Directus headless CMS API. It provides a convenient and
easy-to-use interface for performing CRUD operations, querying data, and managing resources in Directus.

## Features

- Login and authentication handling
- Reading and writing data from Directus collections
- Filtering, sorting, and searching data
- Aggregating data using aggregation operators
- Creating, updating, and deleting items in Directus collections
- Handling multiple users in the same session

## Disclaimer:

**Please note that DirectusPyWrapper is currently under active development and may not be suitable for
production use at this time.**

While efforts are being made to ensure the library's stability and functionality, there
may still be bugs or limitations that need to be addressed. It is recommended to exercise caution and thoroughly test
the library before using it in a production environment. Feedback, bug reports, and contributions are highly appreciated
to help improve the library's reliability and feature set.

## Installation

You can install DirectusPyWrapper using pip:

```shell
pip install git+https://github.com/panos-stavrianos/DirectusPyWrapper.git
```

> PyPI package coming soon!

## Authentication and Session Handling

### Login

Create a Directus instance using email and password

```python
from DirectusPyWrapper import Directus

directus = Directus("https://example.com", email="user@example.com", password="secret")
```

Alternately create a Directus instance using the static token

```python
from DirectusPyWrapper import Directus

directus = Directus("https://example.com", token="static token")
```

### Refresh Token

If you want to refresh the token you can use the `refresh` method

```python
directus.refresh()
```


### Logout

Logout from Directus

```python
directus.logout()
```

Another way is to use the `with` statement to automatically logout when the session ends

```python
with Directus(url, email, password) as directus:
    # do stuff
```

### Multiple Users in the Same Session

You can use multiple users in the same session by creating a new Directus instance by passing the session object

```python
session = requests.Session()
directus1 = Directus(url, token=token, session=session)
directus2 = Directus(url, email=email, password=password, session=session)
```

## Collections

There are two ways to set a collection, either by passing the collection name as a string
or by passing the collection as a Pydantic model.

Using the `items` method you can pass the collection name as a string

```python
directus.items("directus_users")
```

Using the `collection` method you can pass the collection as a `Pydantic` model

```python
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    description: Optional[str]
    email: Optional[str]
    role: Optional[str] | Optional[Role]
    status: Optional[str]
    title: Optional[str]
    token: Optional[str]

    class Config:
        collection = 'directus_users'


directus.collection(User)
```

> Don't forget to set the `collection` attribute in the `Config` class

If you go with the second option, you will get the responses as `Pydantic` models (auto parsing)

> The `items` and `collection` methods are returning a `DirectusRequest` object which is used to perform READ, CREATE,
> UPDATE and DELETE operations

## Reading Data

When you have the DirectusRequest object you can use the `read` method to get the data
This will return a DirectusResponse object which contains the data.

```python
directus.items("directus_users").read()
```

### Filtering

You can filter the data by passing a `Filter` object to the `filter` method

For an easy equality filter you can pass the field name and the value

```python
directus.items("directus_users").filter(first_name="John").read()
```

To add multiple equality filters you can chain the `filter` method

```python
directus.items("directus_users")
.filter(first_name="John")
.filter(last_name="Doe").read()
```

Using it like this you chain the filters with `AND` operator

> Filtering is a little complicated, and it deserves its own section
> so please check the [Filtering](#filtering) section for more details

### Sorting

You can sort the data by passing the field name to the `sort` method

```python
directus.items("directus_users").sort("first_name", asc=True).read()
```

To add multiple sorting fields you can chain the `sort` method

```python
directus.items("directus_users")
.sort("first_name", asc=True)
.sort("last_name", asc=False).read()
```

### Limiting

You can limit the data by passing the limit to the `limit` method

```python
directus.items("directus_users").limit(10).read()
```

### Aggregation

You can aggregate the data by passing the aggregation operator to the `aggregate` method

```python
directus.items("directus_users").aggregate(AggregationOperators.Count).read()
```

The available aggregation operators are:

- Count
- CountDistinct
- CountAll
- Sum
- SumDistinct
- Average
- AverageDistinct
- Minimum
- Maximum

### Grouping

You can group the data by passing the field names to the `group_by` method

```python
directus.items("directus_users").group_by("first_name", "last_name").read()
```

### Searching

You can search the data by passing the search term to the `search` method

```python
directus.items("directus_users").search("John").read()
```

### Selecting Fields

You can select the fields you want to get by passing the field names to the `fields` method

```python
directus.items("directus_users").fields("first_name", "last_name").read()
```

### Getting the Count Metadata

You can get the count of the data (total count and filtered count) calling `include_count`

```python
directus.items("directus_users").include_count().read()
```

## Retrieving items

After you call `read()` you get a `DirectusResponse` object which contains the data.

- `item` for single item
- `items` for multiple items

Getting the data as a dictionary or a list of dictionaries

```python
response = directus.items("directus_users").read()
print(response.item["first_name"])
print(response.items)
```

If you use `collection` you will get the data as a `Pydantic` object or a list of `Pydantic` objects

```python
response = directus.collection(User).read()
print(response.item.first_name)
print(response.items)
```

### Converting to Pydantic or to Dictionary

Apart from the auto parsing, you can manually convert the data to a `Pydantic` object or to a dictionary using:

- `item_as(User)` or `items_as(User)`
- `item_as_dict()` or `items_as_dict()`

```python
response = directus.items("directus_users").read()
print(response.item_as(User))

response = directus.collection(User).read()
print(response.item_as_dict())
```

## Creating Items

For creating the library do not support `Pydantic` models, you have to pass a dictionary

- create_one(item: dict)
- create_many(items: List[dict])

> Very soon the library will support `Pydantic` models for creating items
> and the `create_one` and `create_many` methods will be deprecated
> and replaced with the more broad `create` method

```python
directus.items("directus_users").create_one({
    "first_name": "John", "last_name": "Doe"
})
```

```python
directus.items("directus_users").create_many(
    [
        {"first_name": "John", "last_name": "Doe"},
        {"first_name": "Jane", "last_name": "Doe"}
    ]
)
```

## Updating Items

For updating the library do not support `Pydantic` models, you have to pass a dictionary

- `update_one( id: str|int, item: dict)`
- `update_many( ids: List[str|int], items: List[dict])`

> Supporting `Pydantic` models for updating items is not planned for now

```python
directus.items("directus_users").update_one(1, {
    "first_name": "Red",
    "last_name": "John"
})
```

```python
directus.items("directus_users").update_many(
    [1, 2],
    [
        {"first_name": "Jean-Luc"},
        {"first_name": "Jane", "last_name": "Doe"}
    ]
)
```

## Deleting Items

> Very soon the library will deprecate the `delete_one` and `delete_many` methods
> and replaced them with the more broad `delete` method, accepting a list or a single id

- `delete_one(id: str|int)`
- `delete_many(ids: List[str|int])`

```python
directus.items("directus_users").delete_one(1)
```

```python
directus.items("directus_users").delete_many([1, 2])
```

## Contributing

Contributions to DirectusPyWrapper are welcome! If you find any issues or have suggestions for improvements, please open
an issue. If you'd like to contribute code,
you can fork the repository and create a pull request with your changes.

## License

DirectusPyWrapper is licensed under the [MIT License](https://opensource.org/licenses/MIT).