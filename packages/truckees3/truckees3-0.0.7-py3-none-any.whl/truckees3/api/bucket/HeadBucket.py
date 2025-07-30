import logging
import eons
import apie

class head_bucket(S3Endpoint):
	def __init__(this, name="head_bucket"):
		super().__init__(name)
		this.supportedMethods = ['HEAD']
		this.arg.kw.required.append('bucket_name')
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Checks if a bucket exists.
Example: HEAD /my-bucket-to-check
'''

	async def HandleS3Request(this):
		await this.RequireBucket()
		this.response.headers['x-amz-bucket-region'] = "us-east-1"
		this.response.code = 200
		return