---
title: Get started
---

## Requirements

HapiDeploy requires Python `3.13+`, so you need to check your python version

```bash
python --version
```

## Installation

You can install `hapideploy` library using pip.

```bash
pip install hapideploy==0.1.0.dev7
```

Check if the hapi command is available.

```bash
hapi about
```

If you see the result like below, the installation process is successful.

```plain
Hapi CLI 0.1.0.dev7
```

## Usage

Create `inventory.yml` and `deploy.py` files by running the `init` command. You'll be asked about what recipe you want to use. Just pick one and continue.

```bash
hapi init
```

After that, you can define [remotes](./remotes.md) and [tasks](./tasks.md), then executing them via the `hapi` CLI.

```bash
hapi <command>
```
