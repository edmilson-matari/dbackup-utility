# DBackup

#### Video Demo: https://youtu.be/ga7V6d61EF8

#### Description:

DBackup is a command-line database backup utility written in Python. I created this project as my CS50 Final Project to make the process of creating and storing database backups simpler through an interactive terminal interface.

The application supports three database systems: **MySQL, PostgreSQL, and MongoDB**. When the program starts, the user selects the database system they want to back up and then provides the required connection information. DBackup verifies the database connection before starting the backup process.

For MySQL and PostgreSQL, DBackup uses the database systems' native command-line backup utilities. MySQL backups are created using `mariadb-dump`, while PostgreSQL backups are created using `pg_dump`. MongoDB backups use `mongodump`. Using these native utilities allows the application to rely on tools specifically designed for database backups instead of implementing the complete backup mechanisms itself.

The generated database dumps are compressed using Python's `gzip` module. This reduces the size of the backup files and makes them more convenient to store. Each backup filename also contains a timestamp so that multiple backups can be created without accidentally overwriting previous backups.

DBackup uses the **Questionary** library to provide an interactive terminal experience. It provides database selection menus, confirmation prompts, password input, path selection, and autocomplete. The autocomplete feature stores previously entered values in a local `autocomplete` file and uses them as suggestions the next time the program is executed. This makes frequently used information faster to enter.

The **Rich** library is used to improve the terminal output. It provides formatted panels, colors, and messages that make warnings, successful operations, errors, and other important information easier to distinguish.

The project also includes automatic installation of the required database connectors. Before performing a backup, DBackup checks whether the appropriate Python connector is installed. If it is missing, the program installs it using `pip`.

The main functionality is contained in `project.py`. This file contains the application entry point, credential collection, timestamp generation, database-specific backup functions, file management, and connector installation. The project also contains `test_project.py`, which is used to test the application's functionality, and `requirements.txt`, which lists the Python dependencies required by the project.

I chose to build DBackup as a command-line application because database administration and backup operations are commonly performed through the terminal. This also allowed me to focus on Python programming, subprocess execution, error handling, file management, database connectivity, compression, and automated testing while keeping the application lightweight and practical.

