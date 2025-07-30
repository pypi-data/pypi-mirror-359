import logging
import eons
import apie
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from libtruckeefs import File, Directory

class copy_object(S3Endpoint):
	def __init__(this, name="copy_object"):
		super().__init__(name)
		this.supportedMethods = ['PUT']
		this.arg.kw.required.extend(['bucket_name', 'object_key'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Creates a server-side copy of an object.
Source object is specified in the 'x-amz-copy-source' header.
Example: PUT /dest-bucket/new-copy.jpg
Headers: { "x-amz-copy-source": "/source-bucket/original.jpg?versionId=..." }
''' 

	async def HandleS3Request(this):
		copy_source = this.request.headers.get('x-amz-copy-source')
		if (not copy_source):
			raise apie.OtherAPIError("InvalidRequest", "Missing required header: x-amz-copy-source", 400)
		parsed_source = urlparse(copy_source)
		source_path_str = parsed_source.path.lstrip('/')
		source_version_id = parse_qs(parsed_source.query).get('versionId', [None])[0]
		await this.RequireBucket()
		versioningManager = this.executor.manager.version(
			precursor=this, 
			bucket_name=source_path_str.split('/')[0],
			object_key='/'.join(source_path_str.split('/')[1:]),
			version_id=source_version_id
		)
		source_file = await versioningManager.GetObject()
		if (source_file is None):
			raise apie.OtherAPIError("NoSuchKey", "The specified key does not exist.", 404)

		destination_path = Path(this.bucket_name) / this.object_key
		logging.info(f"Copying from {source_path_str} (version: {source_version_id}) to {destination_path}")
		copied_file = await source_file.Copy(str(destination_path))

		attrs = await copied_file.GetAttr()
		etag = await copied_file.GetXAttr('user.s3.etag')
		last_modified = datetime.fromtimestamp(attrs.get('mtime', 0)).isoformat() + "Z"

		this.xml_root_tag = 'CopyObjectResult'
		this.response_data = {
			"LastModified": last_modified,
			"ETag": f'"{etag}"'
		}
		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return