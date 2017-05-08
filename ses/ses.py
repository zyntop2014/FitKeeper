import boto.ses
import json

with open('aws_key.txt', 'rb') as aws_file:
	lines = aws_file.readlines()
	access_key_id = lines[0].rstrip('\n')
	secret_access_key = lines[1].rstrip('\n')


# Connect to Amazon AWS
conn = boto.ses.connect_to_region("us-east-1",
		aws_access_key_id = access_key_id,
		aws_secret_access_key = secret_access_key)


def verify_email(email_addr='yc3313@columbia.edu'):
	# verify an email address
	conn.verify_email_address(email_addr)

'''
# list the addresses that are currently verified
addr_list = []
res = conn.list_verified_email_addresses()
temp = res['ListVerifiedEmailAddressesResponse']['ListVerifiedEmailAddressesResult']['VerifiedEmailAddresses']
for addr in temp:
	addr_list.append(str(addr))
# print addr_list
'''

def send_request(source='yc2763@nyu.edu', to_address='yc3313@columbia.edu', reply_addresses='yc2763@nyu.edu'):
	# send formatted message
	text_body = 'Hi,'+'\n'+'\n'+'    I want to make friend with you!'
	conn.send_email(source=source,
			    	to_addresses=to_address,
                	reply_addresses=reply_addresses,
                	subject='You have a friend request @FitKeeper!',
                	body=text_body,
                	format='text')
