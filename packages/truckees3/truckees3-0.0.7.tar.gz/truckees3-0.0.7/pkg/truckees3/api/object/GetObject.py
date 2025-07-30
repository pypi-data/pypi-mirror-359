import logging
import hashlib
import eons
import apie
from pathlib import Path

class get_object(S3Endpoint):
	def __init__(this, name="get_object"):
		super().__init__(name)
		this.supportedMethods = ['GET']
		this.arg.kw.required.extend(['bucket_name', 'object_key'])
		this.arg.kw.optional['versionId'] = None
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Retrieves an object from a bucket.
Supports fetching specific versions via the 'versionId' query parameter.
Example: GET /my-bucket/my-photo.jpg
'''

	async def HandleS3Request(this):
		await this.RequireBucket()
		versioningManager = this.executor.manager.version(precursor=this)
		obj = await versioningManager.GetObject()
		if (obj is None):
			raise apie.OtherAPIError("NoSuchKey", "The specified key does not exist.", 404)
		attrs = await obj.GetAttr()
		etag = await obj.GetXAttr('user.s3.etag')
		this.response.headers['ETag'] = f'"{etag}"'
		this.response.headers['Content-Length'] = str(attrs.get('size', 0))
		if (this.versionId):
			 this.response.headers['x-amz-version-id'] = this.versionId
		this.response.content.message = await obj.Read(0, attrs.get('size', 0))
		this.response.code = 200
		this.clobberContent = False
		return this.ProcessResponse()