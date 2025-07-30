import logging
import hashlib
import eons
import apie
from pathlib import Path

class head_object(S3Endpoint):
	def __init__(this, name="head_object"):
		super().__init__(name)
		this.supportedMethods = ['HEAD']
		this.arg.kw.required.extend(['bucket_name', 'object_key'])
		this.arg.kw.optional['versionId'] = None
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Retrieves metadata for an object without returning the object itself.
Example: HEAD /my-bucket/my-photo.jpg
'''

	async def HandleS3Request(this):
		await this.RequireBucket()
		versioningManager = this.executor.manager.version(precursor=this)
		obj = await versioningManager.GetObject()
		if (obj is None):
			this.response.code = 404
			return
		attrs = await obj.GetAttr()
		etag = await obj.GetXAttr('user.s3.etag')
		this.response.headers['ETag'] = f'"{etag}"'
		this.response.headers['Content-Length'] = str(attrs.get('size', 0))
		if (this.versionId):
			 this.response.headers['x-amz-version-id'] = this.versionId
		this.response.code = 200
		return