# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import boto

# <codecell>

conn = boto.connect_sns(
        aws_access_key_id='AKIAJFD5VPO6RFKGTWIA',
        aws_secret_access_key='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')

# <codecell>

#conn.get_topic_attributes('arn:aws:sns:us-east-1:409355352037:EdgeClientUploadCompleted')

#conn.create_topic('test')
'''{u'CreateTopicResponse': {u'CreateTopicResult': {u'TopicArn': u'arn:aws:sns:us-east-1:409355352037:test'},
  u'ResponseMetadata': {u'RequestId': u'fc82ac83-b2ae-5883-9ff3-e59f1c5505ba'}}}'''
topic = 'arn:aws:sns:us-east-1:409355352037:test'
#xx = conn.subscribe('arn:aws:sns:us-east-1:409355352037:test','email','tyleha@gmail.com')

# <codecell>

print type(xx['SubscribeResponse']['ResponseMetadata']['RequestId'])
print xx

# <codecell>

confirm = conn.confirm_subscription(topic, str(xx['SubscribeResponse']['ResponseMetadata']['RequestId']))
print confirm

# <codecell>

%qtconsole

# <codecell>


