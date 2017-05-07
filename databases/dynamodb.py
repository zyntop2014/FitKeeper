import boto, datetime, os
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


def write_dynamo(d):
    """
    Append record to DynamoDB.
    Data to be written to Dynamo:
        uid: ID of user (the "inviter")
        timestamp: time that invitation happens
        partners: Users are invited.
                  A list of IDs
    """
    mytable.put_item(
        data={
            'uid': d['uid'],
            'timestamp': d['timestamp'],
            'partners': d['partners']
        },
        overwrite=True
    )
    return None


def is_in_dynamo(uid):
    """
    Determine whether there's a record in DynamoDB
    with uid as the (hash) key.
    """
    try:
        data = mytable.get_item(uid=uid)
        return True
    except ItemNotFound:
        return False


def query_dynamo(uid):
    """
    Read records from Dynamo.
    Return:
        res: A list of IDs, unicode type.
    """
    try:
        data = mytable.get_item(uid=uid)   # Only one row, so no iterables
        res = data['partners']
    except ItemNotFound:
        return None

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