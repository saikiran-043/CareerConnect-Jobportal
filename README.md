# CareerConnect — Django + MySQL Job Portal

A responsive job portal starter project with job-seeker and employer accounts, job search, job posting, PDF resume uploads, applications, application status tracking, and Django admin.

## Features

- Register/login/logout using Django authentication and hashed passwords
- Job seeker and employer roles
- Search jobs by title/company/description, location, and employment type
- Employer-only create/edit/delete for their own job listings
- Job seeker applications with PDF resume (5 MB maximum) and optional cover letter
- Prevent duplicate applications for the same job
- Employer applicant dashboard and status updates
- Django admin management
- Responsive CSS and MySQL database configuration

## Requirements

- Python 3.11 or newer
- MySQL Server 8.x (or compatible MySQL server)
- VS Code and its Python extension

## 1. Open the project in VS Code

Extract the ZIP, then use **File → Open Folder** and select `careerconnect_job_portal`.

Open **Terminal → New Terminal**.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, you can run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and then use `.venv\Scripts\python.exe` in place of `python`. Alternatively use the VS Code Command Prompt terminal and run `.venv\Scripts\activate.bat`.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 2. Create the MySQL database and user

Start MySQL Server. Log in as a MySQL administrator using MySQL Workbench or:

```bash
mysql -u root -p
```

Run the following SQL. Choose a strong password and use the same value for `DB_PASSWORD` in `.env`.

```sql
CREATE DATABASE careerconnect
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'careerconnect_user'@'localhost'
  IDENTIFIED BY 'replace-with-a-strong-password';

GRANT ALL PRIVILEGES ON careerconnect.*
  TO 'careerconnect_user'@'localhost';

FLUSH PRIVILEGES;
EXIT;
```

Edit `.env` in the project root:

```dotenv
DJANGO_SECRET_KEY=replace-this-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=careerconnect
DB_USER=careerconnect_user
DB_PASSWORD=replace-with-the-same-strong-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

For local development, `DB_HOST=127.0.0.1` is appropriate. If your MySQL setup uses a different port or hostname, update it. Do not commit `.env` to GitHub.

## 3. Create tables and run the site

Run from the folder containing `manage.py`:

```bash
python manage.py check
python manage.py makemigrations jobs
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

- Home/job search: `/`
- Register: `/register/`
- Log in: `/login/`
- Dashboard: `/dashboard/`
- Django admin: `/admin/`

Choose **Job seeker** or **Employer** when registering. Employer accounts can post jobs. Job seekers can apply to active jobs with a PDF resume.

## 4. Add demo jobs

You can create an employer account through the site, log in, and choose **Post a job**. Or log in to `/admin/` and add jobs. If adding through admin, select an employer account for the job.

## 5. Common issues

- **Can't connect to MySQL:** make sure MySQL Server is running and the `.env` database name, username, password, host, and port match your setup.
- **Access denied:** verify the MySQL user exists and has privileges on `careerconnect`.
- **No such table:** run `python manage.py makemigrations jobs` and `python manage.py migrate`.
- **PowerShell activation error:** use the VS Code Command Prompt terminal or call `.venv\Scripts\python.exe` directly.
- **Resume link unavailable:** verify the upload succeeded. Local media serving is enabled only in DEBUG mode; configure private object storage for production.
- **Static CSS missing in production:** run `python manage.py collectstatic --noinput` and configure the deployment to serve `staticfiles`.

## 6. Git and GitHub

Create a new empty repository on GitHub. Do not add a README there if this folder already has one.

```bash
git init
git add .
git status
git commit -m "Build CareerConnect Django job portal"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL. Check `git status` before committing and make sure `.env`, resumes, and other secrets/uploads are not staged. If `.env` was committed accidentally, remove it from Git history and rotate its credentials.

## 7. AWS deployment outline

Recommended architecture for a first production deployment:

- **EC2**: runs Django/Gunicorn
- **Amazon RDS for MySQL**: managed database
- **S3 private bucket**: uploaded resumes and, optionally, static assets
- **Nginx + HTTPS**: reverse proxy and TLS (or use a managed load balancer)
- **Security groups**: allow HTTPS publicly; allow SSH only from your IP; allow MySQL port 3306 only from the EC2 security group

High-level deployment steps:

1. Create an EC2 instance (Ubuntu LTS) and an RDS MySQL database. Set an RDS master password and do not expose RDS publicly.
2. Configure the EC2 security group for SSH from your IP and HTTPS/HTTP as required. Allow RDS inbound 3306 only from the EC2 security group.
3. Install Python, a virtual environment, Git, and Nginx on EC2. Clone your GitHub repository.
4. Install dependencies with `pip install -r requirements.txt`.
5. Configure production environment variables on EC2: `DJANGO_DEBUG=False`, a strong unique `DJANGO_SECRET_KEY`, your real domain/EC2 hostname in `DJANGO_ALLOWED_HOSTS`, and the RDS endpoint/database credentials in `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_PORT`.
6. Configure `CSRF_TRUSTED_ORIGINS` for your HTTPS domain in Django settings before using the production domain.
7. Run `python manage.py migrate`, `python manage.py collectstatic --noinput`, and create an admin user.
8. Run Gunicorn behind Nginx using a systemd service. Configure HTTPS with a valid certificate.
9. Store resumes in a private S3 bucket (not a public bucket); serve them through an authorized download flow or short-lived presigned URLs. Local disk uploads on EC2 are not durable across instance replacement.
10. Set `DJANGO_DEBUG=False`, test login, permissions, uploads, and HTTPS, then review logs and backups.

### Production checklist before public launch

- Set a generated, secret `DJANGO_SECRET_KEY`; never use the development fallback.
- Add your production domain to `ALLOWED_HOSTS`.
- Add a `CSRF_TRUSTED_ORIGINS` setting for your HTTPS site and configure secure cookies.
- Use private storage for resumes and verify that only the relevant employer can access them. This starter's employer applicant page uses local media URLs and is for local development; do not expose uploaded resumes publicly in production.
- Add file-content validation and malware scanning for uploaded documents.
- Configure email, rate limiting, database backups, monitoring, and privacy/retention policies.
- Run `python manage.py check --deploy` and resolve warnings.
- AWS charges may apply for EC2, RDS, storage, data transfer, and public IPv4. Check current pricing and budgets before creating resources; stop/delete resources you no longer need.

## Important implementation notes

- This project uses a custom Django `User` model. Keep `AUTH_USER_MODEL = "jobs.User"` in place and create the first migrations before creating users.
- Do not change `AUTH_USER_MODEL` after creating production data without a migration plan.
- `makemigrations jobs` generates `jobs/migrations/0001_initial.py` for your installed Django version; the generated migration file is intentionally created during setup.
- This is a learning starter. Before commercial use, add tests, logging, private file storage, email verification/password reset, privacy terms, and deployment hardening.
