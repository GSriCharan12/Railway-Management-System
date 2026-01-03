---
description: How to deploy the Railway Management System to Railway.app
---

# Deploying to Railway.app

Follow these steps to deploy your project to the Railway platform.

## 1. Prepare your GitHub Repository
Ensure all your current changes are pushed to your GitHub repository.
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

## 2. Create a Railway Account
- Go to [Railway.app](https://railway.app/) and sign up with your GitHub account.

## 3. Provision a MySQL Database
- In your Railway Dashboard, click **New Project** -> **Provision MySQL**.
- Once created, go to the **Variables** tab of the MySQL service to find your connection details:
    - `MYSQLHOST`
    - `MYSQLUSER`
    - `MYSQLPASSWORD`
    - `MYSQLDATABASE`

## 4. Deploy your Flask App
- Click **New** -> **GitHub Repo** and select your project repository.
- Railway will detect the `Procfile` and `requirements.txt` automatically.

## 5. Set Environment Variables
In the **Variables** tab of your Flask service, add the following (copying values from your MySQL service):
- `DB_HOST`: `${{MySQL.MYSQLHOST}}`
- `DB_USER`: `${{MySQL.MYSQLUSER}}`
- `DB_PASSWORD`: `${{MySQL.MYSQLPASSWORD}}`
- `DB_NAME`: `${{MySQL.MYSQLDATABASE}}`
- `SECRET_KEY`: (Add a random string for JWT)

## 6. Initialize the Database
Since your app requires an initial schema, you will need to run your SQL schema on the Railway MySQL instance.
- You can use the Railway CLI or a tool like MySQL Workbench to connect to the Railway MySQL host and run the contents of `schema.sql`.
- Alternatively, you can temporarily add a route to `app.py` that executes the `schema.sql` file.

## 7. Access your Site
Once the build is successful, Railway will provide a public URL (e.g., `https://your-project.up.railway.app`).
