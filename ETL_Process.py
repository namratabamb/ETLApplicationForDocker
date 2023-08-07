import boto3
import json
import hashlib
import psycopg2

def read_config(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

# Read AWS SQS credentials from the configuration file
sqs_config = read_config('localstack_cred.json')
aws_access_key = sqs_config['aws_access_key']
aws_secret_key = sqs_config['aws_secret_key']
aws_region = sqs_config['aws_region']
queue_name = sqs_config['queue_name']

# Read PostgreSQL credentials from the configuration file
postgres_config = read_config('postgress_cred.json')
db_host = postgres_config['db_host']
db_port = postgres_config['db_port']
db_name = postgres_config['db_name']
db_user = postgres_config['db_user']
db_password = postgres_config['db_password']

# SQS and PostgreSQL clients
sqs = boto3.client('sqs', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)
connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    database=db_name,
    user=db_user,
    password=db_password
) 


def mask_field(field_value):
    # Check if action is encoding or decoding
    if action == "encode":
        # Encode string to ASCII value
        ascii_string = field_value.encode('ascii')

        # Encode ASCII string to base64
        encoded_string = base64.b64encode(ascii_string).decode('utf-8')

        # Return the encoded string
        return encoded_string

    # Else decode the encrypted string
    elif action == "decode":
            
        # Decode base64 encrypted string
        decoded_string = base64.b64decode(field_value).decode('utf-8')

        # Return the decoded string
        return decoded_string

def read_message_from_sqs(queue_url):
    try:
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        return response.get('Messages', [])
    except Exception as e:
        print("Error reading message from SQS:", str(e))
        return []


def process_message(message_body):
    try:
        json_data = json.loads(message_body)

        # Mask PII fields
        json_data['device_id'] = mask_field(json_data['device_id'])
        json_data['ip'] = mask_field(json_data['ip'])
        
        return json_data
    except json.JSONDecodeError:
        print(f"Invalid JSON format: {message_body}")
        return None
    except Exception as e:
        print("Error processing message:", str(e))
        return None


def write_to_postgres(data):
    try:
        cursor = connection.cursor()

        # Flatten the JSON data and insert into the 'postgres table
        insert_query = f"""
        INSERT INTO login_behavior (user_id, login_time, device_id, ip, location)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            data['user_id'],
            data['login_time'],
            data['device_id'],
            data['ip'],
            data['location']
        ))

        connection.commit()
        cursor.close()
        print("Data inserted into the database.")
    except Exception as e:
        print("Error inserting data into the database:", str(e))


def main():
    try:
        queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']

        while True:
            messages = read_message_from_sqs(queue_url)

            if not messages:
                print("Queue is empty.")
                break

            for message in messages:
                message_body = message['Body']
                receipt_handle = message['ReceiptHandle']

                json_data = process_message(message_body)
                if json_data:
                    write_to_postgres(json_data)

                # Delete the processed message from the queue
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

    except Exception as e:
        print("Error occurred:", str(e))


if __name__ == "__main__":
    main()
