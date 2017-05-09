import boto, datetime, os, datetime
import boto.dynamodb2


# Create resource filename
aws_identity_filename = os.path.join(os.path.dirname(__file__), 'aws_identity.txt')


# Read aws_identity.txt file
try:
    with open(aws_identity_filename, 'rb') as aws_file:
        content = aws_file.readlines()
        ACCOUNT_ID = content[0].rstrip('\n').split()[2]
        IDENTITY_POOL_ID = content[1].rstrip('\n').split()[2]
        ROLE_ARN = content[2].rstrip('\n').split()[2]
        aws_file.close()
except IOError:
    with open('databases/aws_identity.txt', 'rb') as aws_file:
        content = aws_file.readlines()
        ACCOUNT_ID = content[0].rstrip('\n').split()[2]
        IDENTITY_POOL_ID = content[1].rstrip('\n').split()[2]
        ROLE_ARN = content[2].rstrip('\n').split()[2]
        aws_file.close()


# Use cognito to setup identity
cognito = boto.connect_cognito_identity()
cognito_id = cognito.get_id(ACCOUNT_ID, IDENTITY_POOL_ID)
oidc = cognito.get_open_id_token(cognito_id['IdentityId'])
sts = boto.connect_sts()
assumedRoleObject = sts.assume_role_with_web_identity(ROLE_ARN, "XX", oidc['Token'])


# Connect to DynamoDB
# ATTENTION: When using Edison, new table need to be authorized, see Week 3.9
client_dynamo = boto.dynamodb2.connect_to_region(
    'us-east-1',
    aws_access_key_id=assumedRoleObject.credentials.access_key,
    aws_secret_access_key=assumedRoleObject.credentials.secret_key,
    security_token=assumedRoleObject.credentials.session_token)


# Connect to Table "GymPlanner"
from boto.dynamodb2.exceptions import ItemNotFound
from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey
DYNAMODB_TABLE_NAME = 'GymPlanner'
mytable = Table(DYNAMODB_TABLE_NAME, connection=client_dynamo)


def write_inv_record(uid_1, uid_2):
    """
    Write invitation record to DynamoDB.
    uid: Partition Key
    partner: Value
    """
    d = {}
    d2 = {}
    now = datetime.datetime.now().isoformat()

    d['uid'] = uid_1
    d['timestamp'] = now
    d['partner'] = uid_2

    d2['uid'] = uid_2
    d2['timestamp'] = now
    d2['partner'] = uid_1

    mytable.put_item(d, overwrite=True)
    mytable.put_item(d2, overwrite=True)
    return None


def query_inv_record(uid):
    """
    Get all invitation records (for rating purposes).
    If no records, return an empty list.
    """
    records = mytable.query_2(uid__eq=uid)
    res = []
    for record in records:
        d = {}
        d['uid'] = record['uid']
        d['timestamp'] = record['timestamp']
        d['partner'] = record['partner']
        res.append(d)
    
    return res 


def append_inv_records(uids):
    """
    Append invitation records to DynamoDB.
    """
    # Get current timestamp, in "YYYY-MM-DD HH:MM:SS" format.
    today = datetime.datetime.today()
    timestamp = str(today.year) + '-' + str(today.month) + '-' + str(today.day) \
                + ' ' + str(today.hour) + ':' + str(today.minute) + \
                str(today.second)
    # Append records to Dynamo
    for uid in uids:
        d = {}
        d['uid'] = uid
        d['timestamp'] = timestamp
        d['partners'] = [v for v in uids if v != uid]
        write_dynamo(d)

    return None


if __name__ == '__main__':
    today = datetime.datetime.today()
    timestamp = str(today.year) + '-' + str(today.month) + '-' + str(today.day) \
                + ' ' + str(today.hour) + ':' + str(today.minute) + \
                str(today.second)
    uid = '1'
    partners = ['2', '3', '4', '5']
    d = {}
    d['uid'] = uid
    d['timestamp'] = timestamp
    d['partners'] = partners

    # write_dynamo(d)
    print query_dynamo('1')