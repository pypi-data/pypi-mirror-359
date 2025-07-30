import logging
import eons
import apie
from datetime import datetime

class list_parts(S3Endpoint):
	def __init__(this, name="list_parts"):
		super().__init__(name)

		this.supportedMethods = ['GET']
		this.arg.kw.required.extend(['bucket_name', 'object_key', 'uploadId'])
		this.arg.kw.optional['max-parts'] = 1000
		this.arg.kw.optional['part-number-marker'] = 0
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Lists the parts that have been uploaded for a specific multipart upload.
Supports pagination via query parameters.

Example: GET /my-bucket/my-large-object.zip?uploadId=...
'''

	async def HandleS3Request(this):
		multipartManager = this.executor.manager.multipart(precursor=this)
		
		# Verify the upload exists.
		uploadDirPath = multipartManager.GetUploadDirPath(this.uploadId)
		try:
			await this.executor.Async(
				Directory.From(this.executor, uploadDirPath, createIfNotExists=False)
			)
		except Exception:
			raise apie.OtherAPIError("NoSuchUpload", "The specified multipart upload does not exist.", 404)

		all_parts = await multipartManager.ListParts()

		# Handle pagination with part-number-marker.
		start_index = 0
		if (this.get('part-number-marker') > 0):
			start_index = next((i for i, part in enumerate(all_parts) if part['PartNumber'] > this.get('part-number-marker')), len(all_parts))

		paginated_parts = all_parts[start_index:]
		is_truncated = len(paginated_parts) > this.get('max-parts')
		limited_parts = paginated_parts[:this.get('max-parts')]

		next_part_number_marker = limited_parts[-1]['PartNumber'] if limited_parts else 0

		# Format the parts for the XML response.
		formatted_parts = []
		for part in limited_parts:
			attrs = part.get('attrs', {})
			formatted_parts.append({
				"PartNumber": str(part['PartNumber']),
				"LastModified": datetime.fromtimestamp(attrs.get('mtime', 0)).isoformat() + "Z",
				"ETag": f'"{part["ETag"]}"',
				"Size": str(attrs.get('size', 0))
			})
			
		this.xml_root_tag = 'ListPartsResult'
		this.response_data = {
			"Bucket": this.bucket_name,
			"Key": this.object_key,
			"UploadId": this.uploadId,
			"PartNumberMarker": this.get('part-number-marker'),
			"NextPartNumberMarker": next_part_number_marker,
			"MaxParts": this.get('max-parts'),
			"IsTruncated": str(is_truncated).lower(),
			"Part": formatted_parts
		}
		
		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return