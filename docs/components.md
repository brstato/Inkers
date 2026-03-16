# Project Components

This document lists the primary entities identified in the application and their mapped MVC components.

## Core Entities

1. **Account**
   - **Model**: `accountmodel.py`
   - **Controller**: `accountcontroller.py`
   - **View**: `accountview.py`
   - *Description*: Manages user account information and settings.

2. **Agenda & Turnos**
   - **Model**: `agendamodel.py`, `agendaturnosmodel.py`
   - **Controller**: `agendacontroller.py`, `agendaturnoscontroller.py`
   - **View**: `agendaview.py`, `agendaturnosview.py`
   - *Description*: Handles scheduling, appointments, and shifts/turns for professionals.

3. **Anamnese**
   - **Model**: `anamnesemodel.py`
   - **Controller**: `anamnesecontroller.py`
   - **View**: `anamneseview.py`, `anamnese_response.py`
   - *Description*: Manages anamnesis (client health history/forms) before procedures.

4. **Client**
   - **Model**: `clientmodel.py`
   - **Controller**: `clientcontroller.py`
   - **View**: `clientview.py`
   - *Description*: Handles client CRM, registries, and associations.

5. **Expenses (Despesas)**
   - **Model**: `despesasmodel.py`
   - **Controller**: `despesascontroller.py`
   - **View**: `despesasview.py`
   - *Description*: Financial tracking and expense management.

6. **Estudio / Site**
   - **Model**: `studiomodel.py`, `sitemodel.py`
   - **Controller**: `studiocontroller.py`, `sitecontroller.py`
   - **View**: `estudioview.py`, `siteview.py`
   - *Description*: Management of the studio profiles and dynamically generated sites for studios.

7. **Main & Login**
   - **Model**: `mainmodel.py`, `loginmodel.py`
   - **Controller**: `maincontroller.py`, `logincontroller.py`
   - **View**: `mainview.py`, `loginview.py`
   - *Description*: Core navigation, dashboard, and authentication flow.

8. **Products & Services**
   - **Model**: `productmodel.py`, `servicemodel.py`
   - **Controller**: `productcontroller.py`, `servicecontroller.py`
   - **View**: `productview.py`, `serviceview.py`
   - *Description*: Management of catalog items, inventory, and offered services.

9. **Professional**
   - **Model**: `professionalmodel.py`
   - **Controller**: `professionalcontroller.py`
   - **View**: `professionalview.py`
   - *Description*: Defines staff, tattoo artists, and their specific roles.

## Utilities & Others
- **`utils/formatcurr.py`**: Currency formatting utilities.
- **`controller/call_api.py`**: A helper controller to abstract external API requests or centralize API bindings.
- **`model/zapmodel.py`**: Likely responsible for WhatsApp integration mechanisms.
