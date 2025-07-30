import logging
import eons
import apie

class abort_multipart_upload(S3Endpoint):
	def __init__(this, name="abort_multipart_upload"):
		super().__init__(name)

		this.supportedMethods = ['DELETE']
		this.arg.kw.required.extend(['bucket_name', 'object_key', 'uploadId'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Aborts a multipart upload and deletes any stored parts.

Example: DELETE /my-bucket/my-large-object.zip?uploadId=...
'''

	async def HandleS3Request(this):
		multipartManager = this.executor.manager.multipart(precursor=this)
		
		# Verify the upload exists before trying to abort.
		uploadDirPath = multipartManager.GetUploadDirPath(this.uploadId)
		try:
			await this.executor.Async(
				Directory.From(this.executor, uploadDirPath, createIfNotExists=False)
			)
		except Exception:
			raise apie.OtherAPIError("NoSuchUpload", "The specified multipart upload does not exist.", 404)
		
		# Delegate to the manager to delete the temp directory.
		await multipartManager.AbortUpload()

		logging.info(f"Aborted multipart upload for UploadId {this.uploadId}")
		
		# On success, return 204 No Content.
		this.response.code = 204
		return