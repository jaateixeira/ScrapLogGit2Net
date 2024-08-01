# Contributor Guide

Welcome to the project! We're excited to have you contribute. This guide will help you get started and ensure that your contributions are aligned with our project's standards.

## Table of Contents
1. [Setting Up Your Development Environment](#setting-up-your-development-environment)
2. [Coding Style](#coding-style)
3. [Logging](#logging)
4. [Progress Bars](#progress-bars)
5. [Git Workflow](#git-workflow)
8. [Contact](#contact)

## Setting Up Your Development Environment

1. **Fork the repository** on GitHub.
2. **Clone your forked repository** to your local machine:
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
