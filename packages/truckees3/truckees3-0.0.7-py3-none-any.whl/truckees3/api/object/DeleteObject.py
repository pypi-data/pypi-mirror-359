import logging
import eons
import apie
from pathlib import Path
from libtruckeefs import File

class delete_object(S3Endpoint):
	def __init__(this, name="delete_object"):
		super().__init__(name)
		this.supportedMethods = ['DELETE']
		this.arg.kw.required.extend(['bucket_name', 'object_key'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Deletes an object. If versioning is enabled, this creates a delete marker.
Example: DELETE /my-bucket/my-photo.jpg
''' 

	async def HandleS3Request(this):
		await this.RequireBucket()
		versioningManager = this.executor.manager.version(precursor=this)
		versioningStatus = await versioningManager.GetVersioningStatus()

		deleteMarkerVersionId = None
		if (versioningStatus == 'Enabled'):
			logging.info(f"Versioning enabled for {this.bucket_name}. Creating delete marker.")
			deleteMarkerVersionId = await versioningManager.DeleteObject()
		else:
			logging.info(f"Versioning not enabled for {this.bucket_name}. Permanently deleting.")
			try:
				objectPath = Path(this.bucket_name) / this.object_key
				file_to_delete = await this.executor.Async(
					File.From(this.executor, str(objectPath), createIfNotExists=False)
				)
				await file_to_delete.Unlink()
			except Exception:
				logging.info(f"Object {this.object_key} did not exist; delete is successful.")
				pass
		
		this.response.code = 204
		if (deleteMarkerVersionId):
			this.response.headers['x-amz-delete-marker'] = "true"
			this.response.headers['x-amz-version-id'] = deleteMarkerVersionId
		return