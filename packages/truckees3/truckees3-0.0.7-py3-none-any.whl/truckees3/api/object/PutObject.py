import logging
import eons
import apie
from pathlib import Path

class put_object(S3Endpoint):
	def __init__(this, name="put_object"):
		super().__init__(name)
		this.supportedMethods = ['PUT']
		this.arg.kw.required.extend(['bucket_name', 'object_key', 'data'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Uploads an object to a specified bucket.
The request body contains the object data. This endpoint is version-aware.
Example: PUT /my-bucket/my-photo.jpg
'''

	async def HandleS3Request(this):
		await this.RequireBucket()
		etag = this.GetEtag(this.data)
		this.response.headers['ETag'] = f'"{etag}"'

		logging.info(f"Checking versioning status for bucket: {this.bucket_name}")
		versioningManager = this.executor.manager.version(precursor=this, etag=etag)
		versioningStatus = await versioningManager.GetVersioningStatus()

		versionId = None
		if (versioningStatus == 'Enabled'):
			logging.info(f"Versioning is enabled for {this.bucket_name}. Using VersioningManager.")
			versionId = await versioningManager.PutObject()
		else:
			logging.info(f"Versioning is not enabled for {this.bucket_name}. Performing direct write.")
			objectPath = Path(this.bucket_name) / this.object_key
			fileToWrite = await this.executor.Async(
				File.From(this.executor, str(objectPath), createIfNotExists=True)
			)
			await this.executor.Async(fileToWrite.Write(0, this.data))
			await this.executor.Async(fileToWrite.SetXAttr('user.s3.etag', etag))
			logging.info(f"Successfully wrote to {objectPath}")

		if (versionId):
			this.response.headers['x-amz-version-id'] = versionId