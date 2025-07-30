import logging
import re
import eons
import apie

class create_bucket(S3Endpoint):
	def __init__(this, name="create_bucket"):
		super().__init__(name)
		this.supportedMethods = ['PUT']
		this.arg.kw.required.append('bucket_name')
		this.arg.kw.optional['LocationConstraint'] = "us-east-1"
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Creates a new bucket (a top-level directory) per the S3 specification.
Example: PUT /my-new-bucket
'''

	async def HandleS3Request(this):
		if (len(this.bucket_name) < 3 or len(this.bucket_name) > 63):
			raise apie.OtherAPIError("InvalidBucketName", "The specified bucket is not valid.", 400)
		if (not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', this.bucket_name)):
			raise apie.OtherAPIError("InvalidBucketName", "The specified bucket is not valid.", 400)
		if ('..' in this.bucket_name or re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', this.bucket_name)):
			raise apie.OtherAPIError("InvalidBucketName", "The specified bucket is not valid.", 400)
		try:
			await this.RequireBucket()
			logging.info(f"Bucket '{this.bucket_name}' already exists.")
		except apie.APIError as e:
			if (e.s3_code == "NoSuchBucket"):
				logging.info(f"Creating bucket '{this.bucket_name}' in location '{this.LocationConstraint}'")
				await this.executor.Async(
					Directory.From(this.executor, this.bucket_name, createIfNotExists=True)
				)
			else:
				raise e

		this.response.headers['Location'] = f"/{this.bucket_name}"
		return