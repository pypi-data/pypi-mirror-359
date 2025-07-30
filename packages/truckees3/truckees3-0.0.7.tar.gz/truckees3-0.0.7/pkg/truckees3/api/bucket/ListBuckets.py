import logging
import eons
import apie
from datetime import datetime

class list_buckets(S3Endpoint):
	def __init__(this, name="list_buckets"):
		super().__init__(name)

		this.supportedMethods = ['GET']
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Returns an S3-compliant XML list of all buckets.
'''

	async def HandleS3Request(this):
		# To list buckets, we list the contents of the root directory.
		root = await this.executor.Async(
			Directory.From(this.executor, "", createIfNotExists=False)
		)
		
		bucket_inodes = await root.List()

		buckets_data = []
		for inode in bucket_inodes:
			# We only care about directories at the top level.
			if (inode.kind == 'Directory'):
				attrs = await inode.GetAttr()
				buckets_data.append({
					"Name": inode.name,
					"CreationDate": datetime.fromtimestamp(attrs.get('ctime', 0)).isoformat() + "Z"
				})

		# In a real system, this would be fetched from a user/session manager.
		owner_info = {
			"ID": "02d6176db174dc93cb1b85225c606de673b4e931e254d88e2e921e4225e7914d",
			"DisplayName": "primary-user"
		}

		this.xml_root_tag = 'ListAllMyBucketsResult'
		this.response_data = {
			"Owner": owner_info,
			"Buckets": { "Bucket": buckets_data }
		}
		
		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return