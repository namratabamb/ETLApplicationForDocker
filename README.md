# ETL Application For Docker #
## This application fetches data from AWS localstack docker image which has a AWS SQS queue, performs ETL and stores the transformed data into a Postgres table. Find the problem statement at the below link:
https://fetch-hiring.s3.amazonaws.com/data-engineer/pii-masking.pdf

## Prerequisites

Before you begin, ensure you have the following installed on your local machine:

- Python 3.x
- Docker (for running the PostgreSQL database)
- AWS CLI (for AWS SQS interaction)
- PostgreSQL client (for database interaction)


## Steps to run the code
1. Clone this repo.
```bash
git clone https://github.com/namratabamb/ETLApplicationForDocker.git
```

2. Go into the cloned repo.
```bash
cd ETLApplicationForDocker
```

3. Install the Python packages.
```bash
pip install -r requirements.txt
```

4. Configure your AWS credentials.
```bash
aws configure
```

5. Run the PostgreSQL using Docker.
```bash
docker-compose up -d
```

6. Assuming the AWS SQS credentials in 'localstack_cred.json' and PostgreSQL credentials in 'postgress_cred.json' are legitimate and valud, we run the main Python program.
```bash
python ETL_Process.py
```

## Decrypting masked PIIs
- The `ip` and `device_id` fields are masked using base64 encryption which is a binary-to-text encoding scheme.
- To recover the encrypted fields, we can use the below command.
```bash
echo -n "<sample_base64_encrypted_string>" | base64 --decrypt
```