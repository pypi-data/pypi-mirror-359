import logging
import eons
import apie

class delete_bucket(S3Endpoint):
	def __init__(this, name="delete_bucket"):
		super().__init__(name)
		this.supportedMethods = ['DELETE']
		this.arg.kw.required.append('bucket_name')
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Deletes a bucket. The bucket must be empty.
Example: DELETE /my-bucket-to-delete
'''

	async def HandleS3Request(this):
		bucket = await this.RequireBucket()
		children = await bucket.List()
		if (len(children) > 0):
			raise apie.OtherAPIError("BucketNotEmpty", "The bucket you tried to delete is not empty.", 409)

		await bucket.Unlink()
		logging.info(f"Successfully deleted bucket: {this.bucket_name}")
		this.response.code = 204
		return