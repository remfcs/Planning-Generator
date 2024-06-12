# Planning Tailor

## Description
In this case, we are examining a project initiated to enhance the efficiency of language section planning, specifically designed for Mary Stephenson, the responsible party for the language section. This initiative roots from the critical need to address the significant time and effort expended in the creation and updating of LV1/LV2 planning, which Mary found unsatisfactory due to its reliance on manual processes such as the use of post-it notes or Excel spreadsheets. These methods, while traditional, are prone to errors, time-consuming, and lack the flexibility required for efficient schedule management.

The sponsor of this project is the organization overseeing the language section, which has identified the inefficiencies and sought a technological solution to streamline the process. This organization, while not detailed in figures, is presumably an educational institution or a language training provider that values innovation and efficiency in its operations. The key elements of this organization likely include a commitment to language education, a structured curriculum that necessitates careful planning of language levels (LV1/LV2), and a dynamic schedule that requires frequent updates.

The genesis of the project came directly from the identified need by Mary Stephenson to improve the planning process within the language section she oversees. The manual methods currently in use were deemed inadequate, leading to the search for a solution that could save time and reduce the margin for error.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Features](#features)
4. [File Structure](#file-structure)
5. [Responsibility report](#Responsibility-report)
6. [Testing](#testing)
7. [Improvement ideas](#Improvement-ideas)
8. [Contributors](#Contributors)

## Installation
To install this project & the dependencies, follow these steps:

1. Clone the repository:
   ```bash
    git clone https://github.com/yourusername/Planning-Generatore.git
    ```

2. Navigate to the project directory:
    ```bash
    cd Planning-Generator
    ```

3.  Install dependencies:

    Need to install Pyhton : [Python](https://www.python.org/downloads/)

4. Create the launch button:
    - Locate the file:
        Open File Explorer and navigate to the file "Planning_Taylor.bat" to create a shortcut.
    
    - Create the shortcut:
        Right-click on the file.
        In the context menu, select Send to and then Desktop (create shortcut).
    
    This will create a shortcut on the desktop pointing to the selected file.


## Usage 

1.  Start the application : click on 'Planning_Taylor'

2. Open your browser and navigate to `http://localhost:5000` or `http://127.0.0.1:5000` if it does not open itself .

3. To close the application : Close the web page and the powershell.


## Features

* Format of the file 
    ### Upload files with students, promotion and LV2

        |-----------------------------------|-------------|-------------|--------------|--------------------|
        | Name of the file                  |       Student_Info        |     + format of the file          |
        |-----------------------------------|-------------|-------------|--------------|--------------------|
        | Column name needed in the file    |  Nom        |  Prénom     |  Mail        |  Programme         |
        |-----------------------------------|-------------|-------------|--------------|--------------------|
        |-----------------------------------|-------------|-------------|-----------------------------------|
        | Name of the file                  |   Student_Sondage_LV2     |     + format of the file          |
        |-----------------------------------|-------------|-------------|-----------------------------------|
        | Column name needed in the file    |  Nom        |  Prénom     |            Langues                |
        |-----------------------------------|-------------|-------------|-----------------------------------|

    ### Upload files of the students marks in LV1 and LV2

        |-----------------------------------|----------|-------------------------|----------------------------|------------------------|
        | Name of the file                  |   Espagnol or Anglais or Allemand  | + "_TT" if it’s extra-time | + format of the file   |
        |-----------------------------------|----------|-------------------------|----------------------------|------------------------|
        | Column name needed in the file    |  Nom     |        Prénom           |   État                     |   Note/10,00           |
        |-----------------------------------|----------|-------------------------|----------------------------|------------------------|

* Other input

    - Number of slots in a day : It's the number of courses possible in a day, currently it is 6.
    - Promotions and Levels Availabilities : Click on the half-days available.
    - Manage Teachers : Import the teachers with their details and availabilities in half-days like the student. 


## File Structure
    ``` 
        Planning-Generator/
        ├── algo_feature/
        │   ├── conflict_function.py            Function to resolve conflict
        │   ├── create_groups_function.py       Function to create the groups of student
        │   ├── database_function.py            Function to interact with the database
        │   ├── db_file_function.py             Function to insert value from the user in the database
        │   └── read_foolder_function.py        Function to create a dataframe with the file
        │        
        ├── back_up/
        │   ├── back_up.py                      Function to create and manage the backup
        │   ├── Reset_db.py                     Function to Reset the database (recreate the table)
        │   └── restore_backup.py               Function to restore the backup database
        │        
        ├── data/
        │   ├── fake_data                       Folder for storing input files with information about the student
        │   │   └── [Other files]
        │   ├── PHX/                            Folder for storing output files with phx format
        │   │   └── [Other files]        
        │   ├── uploads/                        Folder for storing input files with information about the student from the user 
        │   │   └── [Other files]        
        │   ├── xlsx/                           Folder for storing test file
        │   │   └── [Other files]        
        │   ├── backup_database.sqlites3        Backup Database
        │   └── database.sqlites3               Database
        │        
        ├── dist/                               Folder with all the dependencies' libraries 
        │   └── [Other folders & files]         
        │
        ├── env/                                Folder with all file to install or update the dependencies
        │   └── [Other files]
        │
        ├── Graphical_Interface/  
        │   ├── Export/                         Folder with all the feature for the export part
        │   │   ├── export.css
        │   │   ├── Export.html
        │   │   ├── export.js    
        │   │   └── [Other files]        
        │   ├── Home Page/                      Folder with all the feature for the home page part
        │   │   └── [Other files]        
        │   ├── Import/                         Folder with all the feature for the import part
        │   │   └── [Other files]        
        │   ├── last_backup/                    Folder with all the feature for the backup restoration part
        │   │   └── [Other files]        
        │   ├── Modify_student/                 Folder with all the feature for the student modification part
        │   │   └── [Other files]        
        │   ├── Restart schedule calculation/   Folder with all the feature for starting the schedule calculation part
        │   │   └── [Other files]        
        │   ├── sidebar/                        Folder with all the feature for the sidepart part
        │   │   └── [Other files]        
        │   ├── start/                          Folder with all the feature for the starting part
        │   │   └── [Other files]           
        │   │ 
        │   ├── server.py                       File with all the command to start the server in local host automatically
        │   ├── script.js                       File with all the command manage the home page 
        │   └── [Other files]
        │
        ├── main.py                             File tor executing the script of creation of the groups
        ├── start_app.sh                        File for starting the project on MacOs and Linux
        ├── start_app.bat                       File for starting the project on Windows
        ├── README.md
        └── [Other folders]
    ```

## Responsibility report
- Law: The application is hosted locally. All data handled by the application is processed in accordance with privacy laws, protecting the confidentiality and rights of individuals whose data is being used to respect the General Data Protection Regulation (GDPR). 

- Ethic: The application does not take into account the gender or ethnicity of any student or teacher.

- Environnemental impact: The application aims to minimize its environmental impact by ensuring it only consumes energy when it is actively used. This design choice helps reduce unnecessary energy consumption, making the application more eco-friendly. Additionally, the application leverages efficient algorithms and data management techniques to ensure optimal performance, further contributing to reduced energy usage.


## Testing

- Input Validation Tests
    * Empty Input Test: Verify that the algorithm handles cases where the list of students is empty.
    * Invalid Student Data Test: Check how the algorithm manages entries with missing or incorrect student data (e.g., missing names, non-numeric values where numbers are expected).
    * Invalid Class Number Test: Ensure the algorithm correctly handles invalid numbers of classes (e.g., zero or negative numbers).
- Basic Functionality Tests
    * Even Distribution Test: Provide a list of students and a number of classes that divides evenly. Verify that students are distributed evenly among classes.
    * Uneven Distribution Test: Provide a list of students and a number of classes that do not divide evenly. Ensure the algorithm handles the remainder correctly, distributing students as evenly as possible.
    * Single Class Test: Test the scenario where there is only one class available. Verify all students are assigned to that one class.
- Edge Cases Tests
    * More Classes Than Students Test: Ensure the algorithm handles scenarios where there are more classes than students, potentially resulting in some empty classes.
    * Exact Match Test: Provide a number of students that is an exact multiple of the number of classes. Verify that each class has the exact same number of students.
- Performance Tests
    * Large Input Test: Assess the algorithm's performance and correctness with a large list of students and a reasonable number of classes.
    * Scalability Test: Test how the algorithm performs as the number of students and classes increases. Verify that it scales efficiently and maintains performance.
- Integration Tests
    * Database Integration Test: If the algorithm integrates with a database, verify that data is correctly retrieved from and stored in the database.
    * User Interface Test: Ensure that the algorithm correctly integrates with any user interface, providing expected outputs based on user inputs.
- Boundary Condition Tests
    * Minimum Input Test: Verify behavior with the minimum possible number of students and classes (e.g., 1 student and 1 class).
    * Maximum Input Test: Test the algorithm with the maximum expected input size to ensure it handles boundary conditions appropriately.
- Unrandomization and Fairness Tests
    * Unrandom Distribution Test: If the algorithm includes a unrandom element in distributing students, verify that repeated runs produce exatly fair distributions.
    * Fairness Test: Ensure no systemic bias is introduced in group formation if certain attributes of students (e.g., skill level, gender) are considered.
- Error Handling Tests
    * Error Message Test: Verify that appropriate and informative error messages are returned for invalid inputs or exceptional situations.
    * Recovery Test: Test the algorithm’s ability to recover from errors or unexpected situations without crashing.


## Improvement ideas

- User Interface part:
    - Create a visual planning for the User interface instead of a table with all the data inside.
    - Add some other features for the selection table and resolve the few last bug.
    - Upgrade the import of data for the teachers.
    - Verify that all the data are fill to be able to create a new planning.

- Algorithm part:   
    - Associate the rooms with groups and teachers.
    - Make the pop-up and local host open only once instead of two.
    - Send the output automatically to the teachers concerned by mail.
    - Add a button to turn off the server in local when we close the page.


## Contributors

- VERSION 1.0 (Project 4A, P2025):
    - DUMAS DE LA ROQUE Marion
    - FRANCIS Remy
    - GIMOND Théo
    - GOUTARD Léo
    - SAMMUT Justine