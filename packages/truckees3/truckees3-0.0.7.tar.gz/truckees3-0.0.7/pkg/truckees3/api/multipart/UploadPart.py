import logging
import eons
import apie

class upload_part(S3Endpoint):
	def __init__(this, name="upload_part"):
		super().__init__(name)

		this.supportedMethods = ['PUT']
		# The data arg will be fetched from the request body.
		this.arg.kw.required.extend(['bucket_name', 'object_key', 'partNumber', 'uploadId', 'data'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Uploads a part for a multipart upload. The data is in the request body.

Example: PUT /my-bucket/my-large-object.zip?partNumber=1&uploadId=...
'''

	async def HandleS3Request(this):
		multipartManager = this.executor.manager.multipart(precursor=this)
		
		# We can verify the upload exists by checking if its temp directory is there.
		uploadDirPath = multipartManager.GetUploadDirPath(this.uploadId)
		try:
			await this.executor.Async(
				Directory.From(this.executor, uploadDirPath, createIfNotExists=False)
			)
		except Exception:
			raise apie.OtherAPIError("NoSuchUpload", "The specified multipart upload does not exist.", 404)

		# Delegate the actual file part write to the manager.
		await multipartManager.UploadPart()
		
		# Calculate the ETag and return it in the header, as per S3 spec.
		this.response.headers['ETag'] = this.GetEtag(this.data)
		
		logging.info(f"Uploaded part {this.partNumber} for UploadId {this.uploadId}")
		
		# A successful part upload returns 200 OK with an empty body.
		return