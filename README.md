# WikiWSD - Word Sense Disambiguation Library using Wikipedia

The WSD library provides tools to detect words within a text which can be interpreted in multiple ways. All known meanings of those words are pulled from a database and the most likely disambiguation is chosen by evaluating the context of the word. The project is written entirely in Python and contains 4 executable Python scripts:

- `runner.py` reads a text from a plain text file, detects words to be disambiguated and outputs the text into a html file. All required configurations can be entered via a command-line interface.

- `builder.py` provides a simple command-line tool to build the database from a [Wikipedia XML dump](http://en.wikipedia.org/wiki/Wikipedia:Database_download). Please note that this process may take several weeks to finish on a standard PC.

- `evaluator.py` provides a simple command-line tool to evaluate samples from a Wikipedia XML dump by selecting `n` samples randomly and performing a holdout evaluation on them. At the current state, the evaluation of a single article takes between 5 minutes and 2 hours.

- `testrunner.py` executes all unit tests (requires no database).

- `e2etestrunner.py` requires a database set up and performs an end-to-end evaluation test which takes around 5 min.

## Using the modules

Before using the library, a MySQL database has to be set up. The `builder.py` scripts facilitates the setup, but the database has to be created using the following commands:

    CREATE DATABASE `wikiwsd` DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
    GRANT ALL ON `wikiwsd`.* TO `wikiwsd`@`localhost` IDENTIFIED BY 'wikiwsd';
    GRANT ALL ON `wikiwsd`.* TO `wikiwsd`@`%` IDENTIFIED BY 'wikiwsd';

You may change the database name, user and password according to your needs, just make sure to update the `dbsettings.py` file accordingly.

### Building the database
The interactive `builder.py` script should be rather self-explanatory. It allows one to

1. Create the basic database structure (create tables)
2. Create the reference entries for articles by parsing the Wikipedia dump files and resolving redirects
3. Parse the Wikipedia dump file and extract link counts and disambiguations
4. Parse the Wikipedia dump file and extract ngrams for link detection
5. Optimize the database

The steps are recommended to be run in the given order. Each of the three parsing steps may take several days (up to two weeks) to finish.

### Running a sample
In order to test the library, create a plain text file and insert the text to be evaluated. Using the `runner.py` executable, the disambiguation library can be used to process the text and output a human-readable HTML file.

### Evaluating the library
To evaluate the library, the `evaluator.py` script can be used. It allows to select a set of random samples from the Wikipedia dump file and perform a holdout evaluation on them, determining the precision and recall for the two performed steps, finding the words to be disambiguated and disambiguation the possible links separately.

## About
This project was developed as part of my Master program "Software Development and Business Management" at Graz University of Technology. 

### License
This project is published under the MIT License.