# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import boto

# <codecell>

conn = boto.connect_sns(
        aws_access_key_id='AKIAJFD5VPO6RFKGTWIA',
        aws_secret_access_key='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')

# <codecell>

topic = 'arn:aws:sns:us-east-1:409355352037:test'
conn.publish(topic, u'This is a cool message that you are psyched to receive', subject=u'subject line')

# <codecell>


