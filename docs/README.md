# App.Inkers - Project Documentation

## Overview
App.Inkers is a web application built using [Flet](https://flet.dev/), providing both a standalone web server and FastAPI ASGI app export support. The application is designed to serve multiple subdomains, routing users either to the main administrative/app views or to specific studio views depending on the accessed URL.

## Architecture
The project strictly follows the **Model-View-Controller (MVC)** architectural pattern to separate concerns:
- **Model** (`/model`): Handles data logic, database configurations (Zeos DB), and data transfer objects.
- **View** (`/view`): Contains the Flet UI components and page layouts.
- **Controller** (`/controller`): Contains the business logic, tying the Models and Views together.

## Entry Point
The application starts at `main.py`. The `main` asynchronous function sets up the Flet page, configures web properties (`wasm = True`, `pwa = True`), and establishes the routing based on URL parsing.
- If the subdomain is `app`, `devs`, or `dev`, it routes to the administrative and user-specific views (e.g., Login, Main, Agenda, Professional, etc.).
- Otherwise, it falls back to routing to the `EstudioView`, passing the subdomain as the studio name.

## Further Reading
- [Architecture & Conventions](architecture.md)
- [Components](components.md)
- [Database](database.md)
