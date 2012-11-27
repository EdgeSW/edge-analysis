import boto

sqs_connection = boto.connect_sqs(
        aws_access_key_id='AKIAJFD5VPO6RFKGTWIA',
        aws_secret_access_key='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')

def confirm_POST_subscription(conn = None):
    """Function goes to Amazon's SNS to confirm subscription to any given topic. Can easily subscribe via web interface. Requires
       up & running port, etc. Defaults to Tyler's AWS credentials unless supplied with others"""
    if conn == None:
        import boto  
        conn = boto.connect_sns(aws_access_key_id='AKIAJFD5VPO6RFKGTWIA',
            aws_secret_access_key='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')
    
    message = json.loads(request.data)
    if message["Type"] == "SubscriptionConfirmation":
        token = message["Token"]
        topic = message["TopicArn"]
        confirm = conn.confirm_subscription(topic, token)
        print '\n ...subscription confirmed \n'        
    else: print 'not an sns subscription confirmation post'
	
def get_sqs_filename(message):
    '''given a decoded sqs message from SNS, return the Edge filename'''
    
    sqsmessage = json.loads(rs.get_body())["Message"]
    temp = sqsmessage.split('.')
    temp[-1] = 'txt'
    return str('.'.join(temp))