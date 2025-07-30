import logging
import eons
import apie
from pathlib import Path
from datetime import datetime

class list_objects(S3Endpoint):
	def __init__(this, name="list_objects"):
		super().__init__(name)
		this.supportedMethods = ['GET']
		this.arg.kw.required.append('bucket_name')
		this.arg.kw.optional['continuation-token'] = None
		this.arg.kw.optional['delimiter'] = None
		this.arg.kw.optional['max-keys'] = 1000
		this.arg.kw.optional['prefix'] = None
		this.arg.kw.optional['start-after'] = None
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Lists objects within a bucket (ListObjectsV2 API).
Supports pagination and filtering via query parameters.
'''

	async def HandleS3Request(this):
		bucket = await this.RequireBucket()
		all_children = await bucket.List()
		filtered_children = []
		if (this.prefix):
			for child in all_children:
				if (child.upath.startswith(str(Path(this.bucket_name) / this.prefix))):
					filtered_children.append(child)
		else:
			filtered_children = all_children
		filtered_children.sort(key=lambda i: i.upath)

		start_index = 0
		start_key = this.get('start-after') or this.get('continuation-token')
		if (start_key):
			try:
				start_index = next(i for i, child in enumerate(filtered_children) if child.upath == start_key) + 1
			except StopIteration:
				filtered_children = []

		paginated_children = filtered_children[start_index:]
		is_truncated = (len(paginated_children) > this.get('max-keys'))
		limited_children = paginated_children[:this.get('max-keys')]
		next_continuation_token = None
		if (is_truncated):
			next_continuation_token = limited_children[-1].upath

		contents = []
		for inode in limited_children:
			attrs = await inode.GetAttr()
			etag = await inode.GetXAttr('user.s3.etag')
			relative_key = Path(inode.upath).relative_to(this.bucket_name)
			contents.append({
				"Key": str(relative_key),
				"LastModified": datetime.fromtimestamp(attrs.get('mtime', 0)).isoformat() + "Z",
				"ETag": f'"{etag}"',
				"Size": str(attrs.get('size', 0)),
				"StorageClass": "STANDARD"
			})

		this.xml_root_tag = 'ListBucketResult'
		this.response_data = {
			"Name": this.bucket_name,
			"Prefix": this.prefix,
			"MaxKeys": this.get('max-keys'),
			"IsTruncated": str(is_truncated).lower(),
			"Contents": contents
		}

		if (this.get('continuation-token')):
			this.response_data['ContinuationToken'] = this.get('continuation-token')
		if (next_continuation_token):
			this.response_data['NextContinuationToken'] = next_continuation_token

		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return