# mooch

![PyPI](https://img.shields.io/pypi/v/mooch?label=mooch)
![Python Versions](https://img.shields.io/badge/python-3.9+-blue?logo=python)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mooch)](https://pypistats.org/packages/mooch)
[![GitHub issues](https://img.shields.io/github/issues/nickstuer/mooch.svg)](https://github.com/nickstuer/mooch/issues)

![Lines Of Code](https://tokei.rs/b1/github/nickstuer/mooch)
[![Codecov](https://img.shields.io/codecov/c/github/nickstuer/mooch)](https://app.codecov.io/gh/nickstuer/mooch)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/nickstuer/mooch/run_tests.yml)](https://github.com/nickstuer/mooch/actions/workflows/run_tests.yml)

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

### Settings
[`mooch.settings`](https://github.com/nickstuer/mooch.settings) is a seperate Python packaged included in mooch. It is lightweight, TOML-backed configuration/settings utility that that exposes project settings as standard Python dictionaries — allowing you to work with settings in a familiar, Pythonic way.

- TOML-powered: Uses toml under the hood for modern, human-friendly settings files.
- Dictionary-like interface: Access and manipulate settings with regular dict operations.
- Nested access: Supports nested structures and dotted key notation.
- Safe defaults: Easily provide fallback values or defaults when keys are missing from the setting file.
- Optional always reload: Reloads setting file everytime a key is read. (Enabled by default)

### Location
Provide a zip code to get city, state and lat, lon.

### Require
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

### Settings

```python
from mooch.settings import Settings

defaults = {}
defaults["settings.mood"] = "happy"
defaults["settings.volume"] = 50

settings = Settings("mooch", defaults)  # Change 'mooch' to your project's name

print("Current Settings:")
print(f"Mood: {settings.get('settings.mood')}")
print(f"Volume: {settings.get('settings.volume')}")

settings["settings.volume"] = 75

print("Updated Settings:")
print(f"Mood: {settings.get('settings.mood')}")
print(f"Volume: {settings.get('settings.volume')}")
```

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