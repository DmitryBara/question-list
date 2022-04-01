# Run App
```
./scripts/start-container  # Initial step for 
./scripts/migrate          # Apply migrations to database
./scripts/manage test      # Run a testing
./scripts/seed             # Put prepared data to database (user auth data)
./scripts/start-app        # Run application
```

Server will be available on http://0.0.0.0:8000/graphql.
<br />
You could copy-paste requests from this [file](docs/graphql_requests.txt).
<br />
<br />



# TODO's
<br />
1. In addition to returning and order in field ```orderedQuestionIds``` backend also should return ordered data in field ```questionSet```. It will prevent unnecessary sorting on client side before render.
<br />
<br />
2. Implement common error handler for GraphQL API errors.
<br />
<br />
3. Write more test.
<br />
<br />

# Explanations
<br />
1. Some packages are set to strict version in Pipfile because of compatibility problems.
&nbsp;
<br />
<br />
2. Parameter ATOMIC_REQUESTS is set to True on request level.
<br />
With that settings we could do validation in any place of request lifecycle, it works for query and mutations.
<br />
<br />
3. It is my first experience of working with ```graphene``` Python library and I decide to document more than usually.
<br />
 I assume that [this schema file](docs/graphql_requests.txt) should be separated by smallest part of code, like: ```input_arguments.py```, ```graphql_types.py```, etc.
 I just do not have example of good code style in front of me and decide do not rush with it.
<br />
 Anyway you could check [a my work with GraphQL API in Node.js](https://github.com/DmitryBara/task-manager) environment and see how I separate logic there.
<br />
<br />
4. Current project was started from this [a boilreplate](https://github.com/kadenbarlow/django-postgres-graphql-boilerplate).
<br />
<br />
5. Technical assignment available in this [a pdf file](docs/technical_assignment.pdf).
