import boto, datetime
import boto.dynamodb2


# Read aws identity file
try:
    with open('aws_identity.txt', 'rb') as aws_file:
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
from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey
DYNAMODB_TABLE_NAME = 'GymPlanner'
mytable = Table(DYNAMODB_TABLE_NAME, connection=client_dynamo)


def write_dynamo(d):
    """
    Append record to DynamoDB.
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


def read_dynamo(uid):
    """
    Read records from Dynamo. 
    """
    data = mytable.get_item(uid=uid)
    res = data['partners']

    return res


if __name__ == '__main__':
    today = datetime.datetime.today()
    timestamp = str(today.year) + '-' + str(today.month) + '-' + str(today.day)  
    uid = '1'
    partners = ['2', '3', '4', '5']
    d = {}
    d['uid'] = uid
    d['timestamp'] = timestamp
    d['partners'] = partners

    # write_dynamo(d)
    print read_dynamo('1')