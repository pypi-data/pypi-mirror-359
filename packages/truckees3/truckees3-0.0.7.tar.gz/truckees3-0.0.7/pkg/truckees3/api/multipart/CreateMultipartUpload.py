import logging
import eons
import apie

class create_multipart_upload(S3Endpoint):
	def __init__(this, name="create_multipart_upload"):
		super().__init__(name)
		this.supportedMethods = ['POST']
		this.arg.kw.required.extend(['bucket_name', 'object_key'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Initiates a multipart upload and returns an upload ID.
Example: POST /my-bucket/my-large-object.zip?uploads
'''

	async def HandleS3Request(this):
		await this.RequireBucket()
		multipartManager = this.executor.manager.multipart(precursor=this)
		uploadId = await multipartManager.CreateUpload()

		logging.info(f"Initiated multipart upload for {this.object_key} with UploadId: {uploadId}")

		this.xml_root_tag = 'InitiateMultipartUploadResult'
		this.response_data = {
			"Bucket": this.bucket_name,
			"Key": this.object_key,
			"UploadId": uploadId
		}
		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return