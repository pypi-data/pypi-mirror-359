# FSM Storage for Aiogram 3.x

Custom file-based and SQLite-based storage for [Aiogram 3.x](https://github.com/aiogram/aiogram), 
built from scratch without external dependencies.

## Features

- ✅ JSON, Pickle, and SQLite storage implementations
- ✅ Async-safe with locks
- ✅ Compatible with Dispatcher from Aiogram 3.x
- ✅ Simple and lightweight

## Installation

Just copy the storage class you want to use into your project. No pip installation needed.

## Usage

```python
from aiogram import Dispatcher
from json_storage import JSONStorage  # or SQLiteStorage, PickleStorage

dp = Dispatcher(storage=JSONStorage())
