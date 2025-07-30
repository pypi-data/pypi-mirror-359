import logging
import re
import eons
import apie
from datetime import datetime

class upload_part_copy(S3Endpoint):
	def __init__(this, name="upload_part_copy"):
		super().__init__(name)

		this.supportedMethods = ['PUT']
		this.arg.kw.required.extend(['bucket_name', 'object_key', 'partNumber', 'uploadId'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Copies a source object as a part of a multipart upload.
Source is specified via 'x-amz-copy-source' header.
'''

	async def HandleS3Request(this):
		# First, verify the destination multipart upload exists.
		multipartManager = this.executor.manager.multipart(precursor=this)
		uploadDirPath = multipartManager.GetUploadDirPath(this.uploadId)
		try:
			await this.executor.Async(
				Directory.From(this.executor, uploadDirPath, createIfNotExists=False)
			)
		except Exception:
			raise apie.OtherAPIError("NoSuchUpload", "The specified multipart upload does not exist.", 404)

		this.copy_source = this.request.headers.get('x-amz-copy-source')
		if (not this.copy_source):
			raise apie.OtherAPIError("InvalidRequest", "Missing required header: x-amz-copy-source", 400)

		source_path_str = this.copy_source.lstrip('/')

		try:
			source_file = await this.executor.Async(
				File.From(this.executor, source_path_str, createIfNotExists=False)
			)
		except Exception:
			raise apie.OtherAPIError("NoSuchKey", "The specified key does not exist.", 404)

		offset = 0
		source_attrs = await source_file.GetAttr()
		size = source_attrs.get('size', 0)

		this.copy_source_range = this.request.headers.get('x-amz-copy-source-range')
		if (this.copy_source_range):
			match = re.match(r'bytes=(\d+)-(\d+)', this.copy_source_range)
			if (not match):
				raise apie.OtherAPIError("InvalidRange", "The Range header is not valid.", 400)
			start_byte, end_byte = map(int, match.groups())
			offset = start_byte
			size = (end_byte - start_byte) + 1

		source_data = await source_file.Read(offset, size)

		# Get the unquoted ETag from our helper.
		etag = this.GetEtag(source_data)

		# Create a new manager with the necessary context for the part upload.
		# This adheres to the style guide by avoiding an explicit WarmUp() call.
		uploadManager = this.executor.manager.multipart(precursor=this, data=source_data, etag=etag)
		await uploadManager.UploadPart()

		this.xml_root_tag = 'CopyPartResult'
		this.response_data = {
			"LastModified": datetime.fromtimestamp(source_attrs.get('mtime', 0)).isoformat() + "Z",
			"ETag": f'"{etag}"' # Add quotes back for the XML response.
		}
		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return