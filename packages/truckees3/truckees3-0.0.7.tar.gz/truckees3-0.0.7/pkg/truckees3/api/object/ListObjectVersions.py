import logging
import eons
import apie
from pathlib import Path
from datetime import datetime
from libtruckeefs import Directory, Inode
import asyncio

class list_object_versions(S3Endpoint):
	def __init__(this, name="list_object_versions"):
		super().__init__(name)
		this.supportedMethods = ['GET']
		this.arg.kw.required.append('bucket_name')
		this.arg.kw.optional['delimiter'] = None
		this.arg.kw.optional['key-marker'] = None
		this.arg.kw.optional['max-keys'] = 1000
		this.arg.kw.optional['prefix'] = None
		this.arg.kw.optional['version-id-marker'] = None
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Lists metadata about all versions of objects in a bucket.
''' 

	async def HandleS3Request(this):
		bucket = await this.RequireBucket()
		versions_manager = this.executor.manager.version(precursor=this)

		all_items = []
		latest_inodes = await bucket.List()
		try:
			archive_dir_path = versions_manager.GetArchiveDirPath()
			archive_dir = await this.executor.Async(Directory.From(this.executor, archive_dir_path))
			historical_inodes = await archive_dir.List()
		except Exception:
			historical_inodes = []

		async def process_inode(inode, is_latest):
			key = Path(inode.upath).relative_to(this.bucket_name).as_posix() if is_latest else '.'.join(inode.name.split('.')[:-1])
			if (this.prefix and not key.startswith(this.prefix)):
				return None
			attrs = await inode.GetAttr()
			version_id = await inode.GetXAttr(versions_manager.xattr_version_id)
			return { "key": key, "inode": inode, "version_id": version_id or "null", "mtime": attrs.get('mtime', 0), "is_latest": is_latest }

		tasks = [process_inode(i, True) for i in latest_inodes] + [process_inode(i, False) for i in historical_inodes]
		all_items = [item for item in await asyncio.gather(*tasks) if item is not None]
		all_items.sort(key=lambda x: (x['key'], -x['mtime']))
		
		start_index = 0
		if (this.get('key-marker')):
			key_marker = this.get('key-marker')
			version_marker = this.get('version-id-marker')
			for i, item in enumerate(all_items):
				if (item['key'] > key_marker):
					start_index = i
					break
				if (item['key'] == key_marker and (not version_marker or item['version_id'] == version_marker)):
					start_index = i + 1
					break
		
		paginated_items = all_items[start_index:]
		is_truncated = (len(paginated_items) > this.get('max-keys'))
		limited_items = paginated_items[:this.get('max-keys')]
		
		next_key_marker = None
		next_version_id_marker = None
		if (is_truncated):
			last_item = limited_items[-1]
			next_key_marker = last_item['key']
			next_version_id_marker = last_item['version_id']

		versions_result = []
		delete_markers_result = []
		for item in limited_items:
			inode = item['inode']
			attrs = await inode.GetAttr()
			etag = await inode.GetXAttr('user.s3.etag')
			is_delete_marker = await inode.GetXAttr(versions_manager.xattr_delete_marker)
			entry = {
				"Key": item['key'], "VersionId": item['version_id'], "IsLatest": str(item['is_latest']).lower(),
				"LastModified": datetime.fromtimestamp(attrs.get('mtime', 0)).isoformat() + "Z", "ETag": f'"{etag}"' if etag else '""',
				"Size": str(attrs.get('size', 0)), "StorageClass": "STANDARD"
			}
			if (is_delete_marker == "true"):
				delete_markers_result.append(entry)
			else:
				versions_result.append(entry)

		this.xml_root_tag = 'ListVersionsResult'
		this.response_data = {
			"Name": this.bucket_name, "Prefix": this.prefix, "KeyMarker": this.get('key-marker'),
			"VersionIdMarker": this.get('version-id-marker'), "MaxKeys": this.get('max-keys'), "IsTruncated": str(is_truncated).lower(),
			"Version": versions_result, "DeleteMarker": delete_markers_result
		}
		if (next_key_marker):
			this.response_data["NextKeyMarker"] = next_key_marker
			this.response_data["NextVersionIdMarker"] = next_version_id_marker

		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return