import logging
import eons
import apie

class complete_multipart_upload(S3Endpoint):
	def __init__(this, name="complete_multipart_upload"):
		super().__init__(name)

		this.supportedMethods = ['POST']
		this.arg.kw.required.extend(['bucket_name', 'object_key', 'uploadId'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Completes a multipart upload by assembling previously uploaded parts.
Requires an XML body listing the parts and their ETags. 
'''

	async def HandleS3Request(this):
		multipartManager = this.executor.manager.multipart(precursor=this)

		try:
			uploadDirPath = multipartManager.GetUploadDirPath(this.uploadId)
			await this.executor.Async(
				Directory.From(this.executor, uploadDirPath, createIfNotExists=False)
			)
		except Exception:
			raise apie.OtherAPIError("NoSuchUpload", "The specified multipart upload does not exist.", 404)

		root = this.ParseXmlRequest()
		if (root is None):
			raise apie.OtherAPIError("MalformedXML", "Missing or malformed XML in request body.", 400)
		
		parts_from_request = []
		last_part_num = 0 # Keep track of the last part number
		for part_elem in root.findall('Part'):
			part_num = int(part_elem.find('PartNumber').text)

			# S3 Spec: Validate that parts are in ascending order. 
			if (part_num <= last_part_num):
				raise apie.OtherAPIError("InvalidPartOrder", "The list of parts was not in ascending order.", 400)

			parts_from_request.append({
				"PartNumber": part_num,
				"ETag": part_elem.find('ETag').text.strip('"')
			})
			last_part_num = part_num

		stored_parts = await multipartManager.ListParts()
		stored_etags = {part['PartNumber']: part['ETag'] for part in stored_parts}

		for requested_part in parts_from_request:
			part_num = requested_part['PartNumber']
			req_etag = requested_part['ETag']

			if (part_num not in stored_etags or stored_etags[part_num] != req_etag):
				raise apie.OtherAPIError("InvalidPart", "One or more of the specified parts could not be found or the ETag did not match.", 400)

		this.parts = parts_from_request
		
		# The manager now returns a tuple: (success, result)
		success, result = await multipartManager.CompleteUpload()
		
		if (not success):
			# A part failed during assembly. Return 200 OK with an error body.
			# 'result' contains the error details dictionary.
			return this.HandleError(result['Code'], result['Message'], 200)

		# If we reach here, success is True and 'result' is the final Inode.
		newly_completed_file = result
		
		validated_etags = [p['ETag'] for p in parts_from_request]
		final_etag = this.GetMultipartEtag(validated_etags)
		
		this.xml_root_tag = 'CompleteMultipartUploadResult'
		this.response_data = {
			"Location": f"/{this.bucket_name}/{this.object_key}",
			"Bucket": this.bucket_name,
			"Key": this.object_key,
			"ETag": f'"{final_etag}"' # Add quotes for the response 
		}

		await newly_completed_file.SetXAttr('user.s3.etag', final_etag)

		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return