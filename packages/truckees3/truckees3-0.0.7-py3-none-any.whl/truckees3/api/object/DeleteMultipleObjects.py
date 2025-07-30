import logging
import eons
import apie
from pathlib import Path

class delete_multiple_objects(S3Endpoint):
	def __init__(this, name="delete_multiple_objects"):
		super().__init__(name)
		this.supportedMethods = ['POST']
		this.arg.kw.required.append('bucket_name')
		this.allowedNext = ['help']

	def GetHelpText(this):
		return '''\
Deletes multiple objects from a bucket.
The request body must be an XML document listing the keys to delete.
Example: POST /my-bucket
Body: <Delete>...</Delete>
'''

	async def HandleS3Request(this):
		await this.RequireBucket()
		root = this.ParseXmlRequest()
		if (root is None):
			raise apie.OtherAPIError("MalformedXML", "The XML you provided was not well-formed or did not validate.", 400)
		
		quiet_element = root.find('Quiet')
		is_quiet = (quiet_element is not None and quiet_element.text.lower() == 'true')
		keys_to_delete = [obj.find('Key').text for obj in root.findall('Object')]

		versioningManager = this.executor.manager.version(precursor=this)
		versioningStatus = await versioningManager.GetVersioningStatus()

		deleted_results = []
		error_results = []

		for key in keys_to_delete:
			try:
				if (versioningStatus == 'Enabled'):
					deleteManager = this.executor.manager.version(precursor=this, object_key=key)
					await deleteManager.DeleteObject()
				else:
					objectPath = Path(this.bucket_name) / key
					file_to_delete = await this.executor.Async(
						File.From(this.executor, str(objectPath), createIfNotExists=False)
					)
					await file_to_delete.Unlink()
				if (not is_quiet):
					deleted_results.append({"Key": key})
			except Exception as e:
				logging.error(f"Failed to delete {key} in multi-delete operation: {e}")
				error_results.append({ "Key": key, "Code": "InternalError", "Message": str(e) })

		this.xml_root_tag = 'DeleteResult'
		this.response_data = {}
		if (len(deleted_results) > 0):
			this.response_data["Deleted"] = deleted_results
		if (len(error_results) > 0):
			this.response_data["Error"] = error_results

		this.BuildXmlResponse(this.xml_root_tag, this.response_data)
		return