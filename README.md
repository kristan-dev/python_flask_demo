python_flask_demo

## Building Project Locally
### Step 1: Copy Configuration Files
Run the following to setup default configuration files:
- Config file `config.yml` resides in `src/conf`
- Config with real values is not meant to be uploaded with the source code. Only include `conf/config.template.yml`

### Step 2: Build & Launch Database + Airflow Containers
 - Build Web Server and DB container using: `docker-compose -f docker-compose.local.yml up --build`. This will build and launch docker containers for local development. 
 - The default `docker-compose.yml` is used for production deployment.

### Step 3: Configure Database
 - As of writing this, the database container exposes the postgres port to the local port `20040`, so make sure you connect using that port.

## Build Noes
 - When using VSCode and using `launch.json`, make sure you do not put any parameters inside `app.run()`, the launch.json file will take precedence in all flask run settings