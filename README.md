# Getmee-Chat-AI-Agent
# Developer Instructions

This document provides guidelines for developers contributing to this project. 
Following these instructions ensures smooth collaboration and consistent development practices.

---

## 1. Clone the Repository

Clone the project repository to your local machine.

git clone <repository-url>
cd <project-folder>

---

## 2. Create a Feature Branch

All development must be done in a feature branch created from the **dev branch**.

Steps:

1. Switch to dev branch
2. Pull latest updates
3. Create a new feature branch

Commands:

git checkout dev
git pull origin dev
git checkout -b feature/feature-name

Example branch names:

feature-chat-ui  
feature-rag-api  
feature-ingestion-pipeline

---

## 3. Implement the Feature

Develop your assigned task or feature in your feature branch.

Guidelines:
- Write clean and readable code
- Follow the project structure
- Test your code before committing
- Keep commits small and meaningful

---

## 4. Commit Changes

Commit your changes with clear commit messages.

git add .
git commit -m "Add chat UI component"

Use meaningful commit messages that describe what was implemented or changed.

---

## 5. Push the Feature Branch

Push your feature branch to the remote repository.

git push origin feature/feature-name

---

## 6. Create a Pull Request

After completing your feature:

1. Go to the GitHub repository
2. Open the **Pull Requests** section
3. Click **New Pull Request**
4. Select your feature branch
5. Set the target branch as **dev**
6. Submit the Pull Request for review

---

## 7. Code Review and Merge

The repository maintainer will review the Pull Request.

Possible outcomes:
- Approved and merged into **dev**
- Changes requested before merging

Once approved, the feature branch will be merged into the **dev branch**.

---

## 8. Do Not Commit Directly to Main

Developers must **not push code directly to the main branch**.

Development flow used in this project:

feature branch → dev → main

- Feature development happens in feature branches
- All completed work is merged into **dev**
- Final stable version is merged from **dev → main**

---

## 9. Always Pull Latest Changes

Before starting new work, update your local dev branch.

git checkout dev
git pull origin dev

This helps prevent merge conflicts and ensures you are working on the latest code.

---

## Summary Workflow

1. Create feature branch from dev
2. Implement feature
3. Commit changes
4. Push branch
5. Create Pull Request to dev
6. Review and merge





This line is for testing purpose