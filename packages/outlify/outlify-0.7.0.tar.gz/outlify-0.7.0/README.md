<div align="center">

<img src="https://raw.githubusercontent.com/k1shk1n/outlify/main/assets/header.svg" alt="outlify header" width="600">

Structured cli output — beautifully, simply, and dependency-free.

[Overview](#overview) •
[Install](#install) •
[Usage](#usage) •
[Components](#components) •
[License](#license)

<img src="https://raw.githubusercontent.com/k1shk1n/outlify/main/assets/footer.svg" alt="outlify footer" width="600">

[![PyPI](https://img.shields.io/pypi/v/outlify)](https://pypi.org/project/outlify/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/outlify)
![Build](https://github.com/k1shk1n/outlify/actions/workflows/checks.yaml/badge.svg)
![Repo Size](https://img.shields.io/github/repo-size/k1shk1n/outlify)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

</div>

## Overview
**Outlify** is designed with a focus on streamlined log output, making it perfect for cli tools.
It emphasizes lightweight operation and minimal dependencies, ensuring smooth integration
into any project. The second key aspect of **Outlify** is its beautiful and user-friendly
log formatting, designed to enhance readability and provide a pleasant experience
for developers and their users.

## Install
**Outlify** is available as a Python package and can be easily installed via `pip` from [PyPI](https://pypi.org/project/outlify/).

To install, simply run the following command:

```bash
pip install outlify
```
This will automatically install the latest version of **Outlify**.

## Usage
You can view demos of any available modules by running the following command:

```bash
python -m outlify.module_name
```

For example, to view the demo for the **Panel** module:

```bash
python -m outlify.panel
```

## Components
**Outlify** provides simple, elegant components for clean and structured CLI output — with zero dependencies. They help organize information clearly and improve log readability.

Each component is easy to use and comes with built-in demos. See below for examples and usage.

### Static

<details>
<summary>Panels</summary>

To highlight important text by displaying it within a panel, use `Panel`. Here's how:

```python
from outlify.panel import Panel

print(Panel('A very important text', title='Warning'))
```

To display parameters in a structured format, use the `ParamsPanel`:

```python
from outlify.panel import ParamsPanel

parameters = {'parameter1': 'value1', 'parameter2': 'value2'}
print(ParamsPanel(parameters, title='Startup Parameters'))
```

For more details on how to use Panels, see [Panels](https://k1shk1n.github.io/outlify/latest/components/panel/)

</details>

<details>
<summary>Lists</summary>

If you need a simple titled list in structured output, use `TitledList`:

```python
from outlify.list import TitledList

packages = ['first', 'second', 'third']
print(TitledList(packages))
```

For more details on how to use Lists, see [Lists](https://k1shk1n.github.io/outlify/latest/components/list/)

</details>

<details>
<summary>Styles</summary>

To styling text and **Outlify** elements, use `Colors` and `Styles`:

```python
from outlify.style import Colors, Styles

print(f'{Colors.red}{Styles.bold}text')
```

For more details on how to use Style, see [Style](https://k1shk1n.github.io/outlify/latest/components/style/)

</details>
<details>
<summary>Decorators</summary>

You can also use **Outlify's** utility **Decorators**

```python
import time
from outlify.decorators import timer

@timer()
def dummy():
    time.sleep(1)

dummy()
```

For more details on how to use Style, see [Decorators](https://k1shk1n.github.io/outlify/latest/components/decorators/)

</details>

## License
Licensed under the [MIT License, Copyright (c) 2025 Vladislav Kishkin](LICENSE)