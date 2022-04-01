# Run App
```
./scripts/start-container  # Initial step for 
./scripts/migrate          # Apply migrations to database
./scripts/manage test      # Run a testing
./scripts/seed             # Put prepared data to database (user auth data)
./scripts/start-app        # Run application
```

Server will be available on http://0.0.0.0:8000/graphql.

You could copy-paste requests from this [file](docs/graphql_requests.txt).




# TODO's

1. In addition to returning order in field ```orderedQuestionIds```, backend also should return ordered data in field ```questionSet```. It will prevent unnecessary sorting on client side before render.

2. Implement common error handler for GraphQL API errors.

3. Write more test.


# Explanations
1. Technical assignment available in this [pdf file](docs/technical_assignment.pdf). According to that current project was started from this [boilreplate](https://github.com/kadenbarlow/django-postgres-graphql-boilerplate).

2. Some packages are set to strict version in Pipfile because of compatibility problems.

3. Parameter ATOMIC_REQUESTS is set to True on request level.
With that settings we could do validation in any place of request lifecycle, it works for query and mutations.

4. It is my first experience of working with graphene library and I decide to document more than I do usually. <br />
 I assume that [this schema file](docs/graphql_requests.txt) should be separated by smallest part of code, like: ```input_arguments.py```, ```graphql_types.py```, ```etc```. <br /><br />
 I just do not have example of good code style in front of me and decide do not rush with it.
 Anyway you could check [my work with GraphQL API in Node.js](https://github.com/DmitryBara/task-manager) environment and see how I separate logic there.


