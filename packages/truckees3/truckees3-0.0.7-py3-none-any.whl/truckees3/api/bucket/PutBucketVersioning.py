import logging
import eons
import apie

class put_bucket_versioning(S3Endpoint):
	def __init__(this, name="put_bucket_versioning"):
		super().__init__(name)
		this.supportedMethods = ['PUT']
		this.arg.kw.required.extend(['bucket_name', 'Status'])
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Sets the versioning state for a bucket.
Requires an XML body with a 'Status' field ('Enabled' or 'Suspended').
Example: PUT /my-bucket-name?versioning
Body: <VersioningConfiguration><Status>Enabled</Status></VersioningConfiguration>
'''

	async def HandleS3Request(this):
		if (this.Status not in ['Enabled', 'Suspended']):
			raise apie.OtherAPIError(
				"MalformedXML",
				"Invalid 'Status' in request. Must be 'Enabled' or 'Suspended'.",
				400
			)
		await this.RequireBucket()
		versioningManager = this.executor.manager.version(precursor=this)
		await versioningManager.SetVersioningStatus()
		logging.info(f"Set versioning status for '{this.bucket_name}' to '{this.Status}'")
		return