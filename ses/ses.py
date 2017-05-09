import boto.ses
import json, os


aws_key_filename = os.path.join(os.path.dirname(__file__), 'aws_key.txt')


with open(aws_key_filename, 'rb') as aws_file:
	lines = aws_file.readlines()
	access_key_id = lines[0].rstrip('\n')
	secret_access_key = lines[1].rstrip('\n')


# Connect to Amazon AWS
def conn_ses():
    """
	Connect to ses.
	"""
    conn = boto.ses.connect_to_region("us-east-1",
			aws_access_key_id = access_key_id,
			aws_secret_access_key = secret_access_key)
    return conn


def verify_email(conn, email_addr='yc3313@columbia.edu'):
	# verify an email address
	conn.verify_email_address(email_addr)
	return None

'''
# list the addresses that are currently verified
addr_list = []
res = conn.list_verified_email_addresses()
temp = res['ListVerifiedEmailAddressesResponse']['ListVerifiedEmailAddressesResult']['VerifiedEmailAddresses']
for addr in temp:
	addr_list.append(str(addr))
# print addr_list
'''

def is_email_verified(conn, user_email):
    """
	Determine if user's email varified by AWS.
	"""
    addr_list = []
    res = conn.list_verified_email_addresses()
    temp = res['ListVerifiedEmailAddressesResponse']['ListVerifiedEmailAddressesResult']['VerifiedEmailAddresses']
    for addr in temp:
		addr_list.append(str(addr))
	
    return True if user_email in addr_list else False


def ses_verification(conn, user_email):
    if not is_email_verified(conn, user_email):
    	verify_email(conn, user_email)
        print "[SES] Sent SES Verification."
    else:
    	print "[SES] This email address has been verified."
	return None


def send_request(conn, source='yc2763@nyu.edu', to_address='yc3313@columbia.edu', reply_addresses='yc2763@nyu.edu'):
	# send formatted message
	text_body = 'Hi,'+'\n'+'\n'+'    I want to make friend with you!'
	conn.send_email(source=source,
			    	to_addresses=to_address,
                	reply_addresses=reply_addresses,
                	subject='You have a friend request @FitKeeper!',
                	body=text_body,
                	format='text')
	return None