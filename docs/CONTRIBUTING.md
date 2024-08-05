# Contributor Guide

Welcome to the project! We're excited to have you contribute to ScrapLogGit2Net. This guide will help you get started and ensure that your contributions are aligned with our project's standards.

## Table of Contents
1. [Setting Up Your Development Environment](#setting-up-your-development-environment)
2. [Coding Style](#coding-style)
3. [Architecture](#architecture)
4. [Logging](#logging)
5. [Progress Bars](#progress-bars)
6. [Git Workflow](#git-workflow)
7. [Easy hacks] [#easy-hacks]
8. [Contact](#contact)

## Setting Up Your Development Environment

1. **Fork the repository** on GitHub.
   To fork the ScrapLogGit2Net repository on GitHub, go to [https://github.com/jaateixeira/ScrapLogGit2Net/](https://github.com/jaateixeira/ScrapLogGit2Net/) . In the top right corner of the page, you will see a "Fork" button. Click on this button, and GitHub will create a copy of the repository under your GitHub account. This forked repository is now independent of the original repository, allowing you to freely make changes without affecting the original project. You can then clone your forked repository to your local machine, make your changes, and push them back to your fork on GitHub.

3. **Clone your forked repository** to your local machine:
   ```bash
   git clone https://github.com/jaateixeira/ScrapLogGit2Net.git

2. Install the dependencies
   See dependencies.sh

## Coding Style 

PEP 8 is the style guide for writing clean, readable Python code. See 
### PEP 8 Coding Style Guide

PEP 8 is the style guide for Python code. It promotes readability and consistency in Python codebases. Following these guidelines will help improve the readability and maintainability of your code.

For the full PEP 8 documentation, please visit the official page: [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)

#### Using flake8 for PEP 8 Compliance

`flake8` is a tool that checks your Python code against the PEP 8 style guide. It helps identify and fix stylistic issues in your code.

#### Setting Up flake8

To install `flake8`, run the following command:

```bash
pip install flake8
```
#### To check your Python files for PEP 8 compliance, navigate to your project directory and run:

```bash
flake8 your_module.py
```


## Project Architecture

The ScrapLogGit2Net project leverages several powerful Python libraries to achieve its functionality. This section provides an overview of the key libraries used and how they fit into the project's architecture.

### NumPy

**NumPy** is used for numerical operations, including the creation and manipulation of arrays and matrices. It provides support for large multi-dimensional arrays and matrices, along with a collection of mathematical functions to operate on these arrays efficiently.

- **Usage**: NumPy is typically used for data manipulation, mathematical calculations, and handling large datasets.
- **Documentation**: [NumPy Documentation](https://numpy.org/doc/stable/)

### NetworkX

**NetworkX** is utilized for creating, manipulating, and studying the structure, dynamics, and functions of complex networks. It allows for the creation of both undirected and directed graphs, along with various algorithms to analyze them.

- **Usage**: NetworkX is used for constructing and analyzing network graphs, which is a core part of the project's functionality.
- **Documentation**: [NetworkX Documentation](https://networkx.org/documentation/stable/)

### Matplotlib

**Matplotlib** is a plotting library used for creating static, interactive, and animated visualizations in Python. It is heavily used for generating plots, charts, and other graphical representations of data.

- **Usage**: Matplotlib is used to visualize data, such as network graphs and other statistical plots.
- **Documentation**: [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)

### Argparse 

### Rich
 the ScrapLogGit2Net repository on GitHub, go to https://github.com/jaateixeira/ScrapLogGit2Net/ . In the top right corner of the page, you will see a "Fork" button. Click on this button, and GitHub will create a copy of the repository under your GitHub account. This forked repository is now independent of the original repository, allowing you to freely make changes without affecting the original project. You can then clone your forked repository to your local machine, make your changes, and push them back to your fork on GitHub.


**Rich** is a library for rich text and beautiful formatting in the terminal. It is used to create aesthetically pleasing and user-friendly command-line interfaces with features like progress bars, tables, and syntax highlighting.

- **Usage**: Rich is used to enhance the terminal output, making it more informative and visually appealing, especially for progress indicators and formatted output.
- **Documentation**: [Rich Documentation](https://rich.readthedocs.io/en/stable/)


**Rich** is used for 

Printing colored text in the console (e.g., debug information)
Printing tex in the MarkDown format for better 
Priting emojis that reflect feeling in the console 
Inspect function to help you learn about objects
Colored Logging in integration Loguru 
Good looking Tables
Progress Bars and Wait Spinners
Better Looking Errors, with colored stacks 

See (https://www.youtube.com/watch?v=JrGFQp9njas)(https://www.youtube.com/watch?v=JrGFQp9njas) for a video tutorial 

### Loguru

**Loguru** is a library designed for simple and effective logging. It simplifies the process of logging by providing an easy-to-use and powerful logging mechanism.

- **Usage**: Loguru is used to handle logging throughout the project, ensuring that logs are informative, easy to read, and useful for debugging.
- **Documentation**: [Loguru Documentation](https://loguru.readthedocs.io/en/stable/)

### Integration and Workflow

The integration of these libraries follows a well-structured workflow:
1. **Data Handling**: NumPy is used to preprocess and handle data efficiently.
2. **Network Construction**: NetworkX is used to construct and manipulate network graphs from the data.
3. **Visualization**: Matplotlib is used to create visual representations of the network graphs and other data.
4. **User Interface**: Rich is used to create an enhanced command-line interface for better user interaction.
5. **Logging**: Loguru is used throughout the project to log important information, errors, and debugging details.

By leveraging these libraries, ScrapLogGit2Net achieves a robust, efficient, and user-friendly architecture that simplifies complex data operations, network analysis, visualization, and interaction.

For more detailed guidelines on how to contribute to the project, please refer to the rest of the `CONTRIBUTING.md` file.

Thank you for your contributions and helping improve ScrapLogGit2Net!










Thank you for your interest in contributing to ScrapLogGit2Net! To ensure a smooth contribution process, please follow the instructions below to submit a pull request with a feature branch.

## Git Workflow
1. [Fork the Repository](#fork-the-repository)
2. [Clone the Forked Repository](#clone-the-forked-repository)
3. [Create a Feature Branch](#create-a-feature-branch)
4. [Make Your Changes](#make-your-changes)
5. [Commit Your Changes](#commit-your-changes)
6. [Push Your Feature Branch](#push-your-feature-branch)
7. [Create a Pull Request](#create-a-pull-request)
8. [Respond to Feedback](#respond-to-feedback)

### Fork the Repository

1. Go to the [ScrapLogGit2Net repository](https://github.com/jaateixeira/ScrapLogGit2Net) on GitHub.
2. Click the **Fork** button in the upper right corner of the page. This will create a copy of the repository under your GitHub account.

### Clone the Forked Repository

1. Open your terminal or command prompt.
2. Clone your forked repository to your local machine:
   ```bash
   git clone https://github.com/your-username/ScrapLogGit2Net.git


Sync your fork:

bash

git checkout main
git pull upstream main
git push origin main

### Create a Feature Branch 
Create a new branch for your feature/bugfix:

bash

git checkout -b feature-branch

Make your changes and commit them:

bash

git add .
git commit -m "Description of your changes"

Push your branch to GitHub:

bash

git push origin feature-branch


### Submitting a Pull Request

    Go to your fork on GitHub.
    Click on the "New Pull Request" button.
    Select the base fork and branch (our repository's main branch) and compare it with your feature-branch.
    Create the pull request with a clear and detailed description of your changes.

### Code Review Process

Once you submit your pull request, it will be reviewed by the project maintainers. Here’s what to expect:

    Initial Review: We will review your code for adherence to the coding standards and overall implementation.
    Feedback: You might receive feedback or requests for changes.
    Approval: Once your pull request passes review, it will be merged into the main branch.

Please be responsive to feedback and make the necessary changes promptly to expedite the review process.


## Contact

## Easy Hacks


