import logging
import eons
import apie

class get_bucket_versioning(S3Endpoint):
	def __init__(this, name="get_bucket_versioning"):
		super().__init__(name)
		this.supportedMethods = ['GET']
		this.arg.kw.required.append('bucket_name')
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Gets the versioning configuration for a bucket.
Example: GET /my-bucket-name?versioning
'''

	async def HandleS3Request(this):
		await this.RequireBucket()
		versioningManager = this.executor.manager.version(precursor=this)
		status = await versioningManager.GetVersioningStatus()
		this.xml_root_tag = 'VersioningConfiguration'
		if (status == 'Enabled' or status == 'Suspended'):
			 this.response_data = { "Status": status }
		else:
			 this.response_data = {}
		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return