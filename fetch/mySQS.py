import boto
import json
from boto.sqs.message import Message, RawMessage


def confirm_POST_subscription(conn = None):
    '''Function goes to Amazons SNS to confirm subscription to any given topic. Can easily subscribe via web interface. Requires
       up & running port, etc. Defaults to Tylers AWS credentials unless supplied with others'''
    assert conn, "Please provide a boto SNS connection object"    
    message = json.loads(request.data)
    if message["Type"] == "SubscriptionConfirmation":
        token = message["Token"]
        topic = message["TopicArn"]
        confirm = conn.confirm_subscription(topic, token)
        print '\n ...subscription confirmed \n'        
    else: print 'not an sns subscription confirmation post'
	
def get_sqs_filename(message):
    '''given a decoded sqs message from SNS, return the Edge filename'''
    
    sqsmessage = json.loads(message.get_body())["Message"]
    temp = sqsmessage.split('.')
    temp[-1] = 'txt'
    return str('.'.join(temp))
	
def approx_total_messages(q):
	'''Running this function ~1000x on a queue containing 1 message returned 
	total num messages==1 all 1000 times. Appears to be trustworthy on boolean check'''
	return sum(int(q.get_attributes()[v]) for v in ['ApproximateNumberOfMessages','ApproximateNumberOfMessagesDelayed','ApproximateNumberOfMessagesNotVisible'])
    
def append_to_queue(content, queue, raw=False): 
    '''Queues a message to SQS with a specific message'''
    body = json.dumps(content)
    m = RawMessage() if raw else Message()
    m.set_body(body)
    receipt = queue.write(m)
    return receipt


###