# mooch

![PyPI](https://img.shields.io/pypi/v/mooch?label=mooch)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mooch)
<img alt="GitHub Issues or Pull Requests" src="https://img.shields.io/github/issues/nickstuer/mooch">

![Python Versions](https://img.shields.io/badge/python-3.9+-blue?logo=python)
![Lines Of Code](https://tokei.rs/b1/github/nickstuer/mooch)
![Codecov](https://img.shields.io/codecov/c/github/nickstuer/mooch)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/nickstuer/mooch/run_tests.yml)

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![license](https://img.shields.io/github/license/nickstuer/mooch.svg)](LICENSE)

mooch is a lightweight Python utility library designed to streamline common development tasks needed for every python project — file handling, path operations, logging decorators, and more — all in one convenient minimum package.

## Table of Contents

- [Features](https://github.com/nickstuer/mooch?tab=readme-ov-file#-features)
- [Install](https://github.com/nickstuer/mooch?tab=readme-ov-file#-install)
- [Usage](https://github.com/nickstuer/mooch?tab=readme-ov-file#-usage)
- [Contributing](https://github.com/nickstuer/mooch?tab=readme-ov-file#-contributing)
- [License](https://github.com/nickstuer/mooch?tab=readme-ov-file#-license)

## ✨ Features

### Location Class
Provide a zip code to get city, state and lat, lon.

### Require Class
Raise an exception if the installed python version is not compatible with a script.
Raise an exception if the desired operating system is not compatible with a script.

### Logging Decorators
**`@log_entry_exit`**
  - Logs the entry and exit of the function, including the arguments.
  - Useful for debugging and tracing.

### Function Decorators
**`@silent(fallback="fallback value")`**
  - Suppresses exceptions raised within the decorated function.
  - Returns `fallback` if an exception is caught.

**`@retry(3)`**
  - Retries the decorated function if an exception is raised.
  - Returns the last exception on final retry attempt. Optional `fallback` returned instead if desired.
  - Set delay time between tries with `delay` argument.


## 🛠 Install

```
pip install mooch
```
or
```
uv add mooch
```

###  📌 Dependencies
Python 3.9 or greater

## 💡 Usage

Browse the examples folder for more examples.

### Logging Decorator

```python
from mooch.decorators import log_entry_exit

@log_entry_exit
def random_function(arg1, arg2):
    print(arg1)
    print(arg2)
```
Log File Output:
```
DEBUG:__main__:Entering: random_function with args=('Hello', 'World'), kwargs={}
DEBUG:__main__:Exiting: random_function
```

### Retry Decorator

```python
from mooch.decorators import retry

@retry(3)
def get_age(name="random_person"):
    age = ...some other task...
    return age
```

### Location
```python
from mooch import Location
location = Location(62704).load()

print(location.city)                # "Springfield"
print(location.state)               # "Illinois"
print(location.state_abbreviation)  # "IL"
print(location.latitude)            # "39.7725"
print(location.longitude)           # "-89.6889"
```

### Require
Raise an Exception if the requirement isn't satisified.
```python
from mooch import Require

Require.python_version("3.13")
Require.operating_system("Windows")
```

## 🏆 Contributing

PRs accepted.

If editing the Readme, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

#### Bug Reports and Feature Requests
Please use the [issue tracker](https://github.com/nickstuer/mooch/issues) to report any bugs or request new features.

#### Contributors

<a href = "https://github.com/nickstuer/mooch/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=nickstuer/mooch"/>
</a>

## 📃 License

[MIT © Nick Stuer](LICENSE)