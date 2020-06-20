# Umba Backend Homework Assignment

## Introduction

Imagine a system where hundreds of thousands of hardware devices are concurrently uploading temperature and humidity sensor data.

The API to facilitate this system accepts creation of sensor records, in addition to retrieval.

These `GET` and `POST` requests can be made at `/devices/<uuid>/readings/`.

Retrieval of sensor data should return a list of sensor values such as:

```
    [{
        'date_created': <int>,
        'device_uuid': <uuid>,
        'type': <string>,
        'value': <int>
    }]
```

The API supports optionally querying by sensor type, in addition to a date range.

A client can also access metrics such as the max, median and mean over a time range.

These metric requests can be made by a `GET` request to `/devices/<uuid>/readings/<metric>/`

When requesting max or median, a single sensor reading dictionary should be returned as seen above.

When requesting the mean, the response should be:

```
    {
        'value': <mean>
    }
```

The API also supports the retrieval of the 1st and 3rd quartile over a specific date range.

This request can be made via a `GET` to `/devices/<uuid>/readings/quartiles/` and should return

```
    {
        'quartile_1': <int>,
        'quartile_3': <int>
    }
```

Finally, the API supports a summary endpoint for all devices and readings. When making a `GET` request to this endpoint, we should receive a list of summaries as defined below, where each summary is sorted in descending order by number of readings per device.

```
    [
        {
            'device_uuid':<uuid>,
            'number_of_readings': <int>,
            'max_reading_value': <int>,
            'median_reading_value': <int>,
            'mean_reading_value': <int>,
            'quartile_1_value': <int>,
            'quartile_3_value': <int>
        },

        ... additional device summaries
    ]
```

The API is backed by a SQLite database.

## Getting Started

This service requires Python3. To get started, create a virtual environment using Python3.

Then, install the requirements using `pip install -r requirements.txt`.
If windows please use: `pip install -r requirements_windows.txt`.

Finally, run the API via `python app.py`.

## Testing

Tests can be run via `pytest -v`.

## Tasks

Your task is to fork this repo and complete the following:

- [x] Add field validation. Only _temperature_ and _humidity_ sensors are allowed with values between _0_ and _100_.
- [x] Add logic for query parameters for _type_ and _start/end_ dates.
- [x] Implementation
  - [x] The max, median and mean endpoints.
  - [x] The quartiles endpoint with start/end parameters
  - [x] Add the path for the summary endpoint
  - [x] Complete the logic for the summary endpoint
- [x] Tests
  - [x] Wrap up the stubbed out unit tests with your changes
  - [x] Add tests for the new summary endpoint
  - [x] Add unit tests for any missing error cases
- [x] README
  - [x] Explain any design decisions you made and why.
  - [x] Imagine you're building the roadmap for this project over the next quarter. What features or updates would you suggest that we prioritize?

When you're finished, send your git repo link to engineering@umba.com. If you have any questions, please do not hesitate to reach out!

## Excercise Rational and decisions

### Decision

Since I haven't so much experience in Flask, I opted to go for optional route parameters described and explained from different sources.

For the statistical operations, I decided to use Pandas library, since it has already the functions and implementations needed, is a natural candidate and personally I think is best suited to tackle the current challenge.

And finally I decided to centralize some of the code inside an utils folder, In this way it will be simple to reuse and manage code in the project.

### Suggestions and TODOs

The first thing would be try to use a class to attend the APIs endpoints, so we may use mixins, this in order to reuse several code, validators and place default values.

Also implement the min and mode endpoints, since those were contempled by the test but not as part of the challenge.

Therefore, I think it would be a better/smarter way to refactor the optional parameters in flask.

And finally foster and improve the tests. The tests are the natural documentation of the code, it explains in a formal language (unambigous) what the application must to do.
