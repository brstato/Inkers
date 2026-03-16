# Architecture & Conventions

## Model-View-Controller (MVC) Pattern
The application uses a standard MVC architecture. Every major entity in the system (e.g., Account, Client, Product, Professional) has a corresponding Model, View, and Controller.

### 1. View Layer (`/view`)
Views are responsible strictly for the UI representation using Flet framework components.
- Each view typically accepts the `page` object from Flet.
- Views build the layout and bind UI events to Controller methods.
- Layouts are composed of components tailored for WEB/PWA display.
- **Examples**: `LoginView`, `MainView`, `AgendaView`.

### 2. Controller Layer (`/controller`)
Controllers contain the business logic of the application.
- They listen to actions triggered by the View.
- They manipulate the Model state or retrieve data from it.
- They format the data and update the View accordingly.
- **Examples**: `accountcontroller.py`, `productcontroller.py`.

### 3. Model Layer (`/model`)
Models handle the data layer, including structures, API calls, and database transactions operations.
- `dto.py` might define data transfer objects for API contracts.
- `config.py` can store configurations for the environment and database endpoints.
- **Examples**: `clientmodel.py`, `servicemodel.py`.

## Routing System
Routing is managed centrally in `main.py` via an asynchronous `route_change` handler. Deep links and view transitions (e.g., `/main`, `/account`, `/agenda`) append specific `View` classes to the `page.views` stack in Flet, allowing straightforward navigation and backward popping (`view_pop`).

## Best Practices
- Keep Views devoid of heavy business logic computations.
- Ensure all databased queries are encapsulated inside Models.
- Manage error handling gracefully in the Controllers.
