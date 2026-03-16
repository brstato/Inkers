# Database Overview

## Structure and Configuration

The application database relies predominantly on SQL-based systems. A major chunk of the schema details and updates are maintained via raw SQL scripts found under the `database/` and top-level directories:
- `database/estrutura_banco.sql`: An initialization script for database structural requirements.
- `update_full_structure.sql`: A comprehensive update script for syncing schema configurations.

## Architecture Integration
- The application uses the **Model layer (`/model`)** to encapsulate database transactions. 
- API calls and models might interface with an external backend if the local database acts merely as a client layer (as implied by parts of `call_api.py` and prior context indicating failure in Zeos database connections externally context).

## Backups & Sync Utilities
There are automation scripts included in the root directory associated with database operations and deployments:
- `backup_banco.sh`: Shell script to automate the backup process of the database.
- `sync_full_inkers.py`: A complex sync task running cross-platform/DB checks.
- `update_full_structure_report.txt`: Outputs the results of the schema updates.

*It is recommended to inspect `update_full_structure.sql` for the most accurate and up-to-date schema definitions and foreign-key constraints applied to entities like Users, Professionals, Agendas, and Studios.*
