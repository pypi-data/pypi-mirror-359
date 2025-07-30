import logging
import uuid
import hashlib
import xml.etree.ElementTree as ET
import eons
import apie
from libtruckeefs import Directory

# A base class for S3-compliant endpoints.
# It handles asynchronous request processing, XML parsing, and standard S3 error formats. 
class S3Endpoint(apie.Endpoint):
	def __init__(this, name="S3Endpoint"):
		super().__init__(name)
		this.mime = 'application/xml'
		this.s3_namespace = "http://s3.amazonaws.com/doc/2006-03-01/"
		this.fetch.possibilities.append('request_xml')
		this.fetch.use.insert(1, 'request_xml')
		this.xml_request_root = None

	def Call(this):
		try:
			this.executor.Async(this.HandleS3Request())
			return this.ProcessResponse()
		except apie.APIError as e:
			logging.warning(f"Returning known error: {e.s3_code}")
			return this.HandleError(e.s3_code, e.message, e.http_status_code)
		except Exception as e:
			logging.error(f"An unexpected error occurred: {e}", exc_info=True)
			return this.HandleError(
				s3_code="InternalError",
				message="We encountered an internal error. Please try again.",
				http_status_code=500
			)

	async def HandleS3Request(this):
		this.response.code = 200
		this.response.content.message = ""
		return

	# Fetches a bucket and confirms it exists, returning the Directory object.
	# Raises "NoSuchBucket" if the directory cannot be found.
	async def RequireBucket(this):
		try:
			# Fetch the directory and return it on success.
			bucket = await this.executor.Async(
				Directory.From(this.executor, this.bucket_name, createIfNotExists=False)
			)
			return bucket
		except Exception:
			# Raise the standard S3 error if it's not found.
			raise apie.OtherAPIError("NoSuchBucket", "The specified bucket does not exist.", 404)

	def GetEtag(this, data):
		if (not data):
			return ''
		m = hashlib.md5()
		m.update(data)
		return m.hexdigest()

	def GetMultipartEtag(this, etags):
		if (not etags):
			return ''
		binary_digests = b''.join([bytes.fromhex(etag.strip('"')) for etag in etags])
		m = hashlib.md5()
		m.update(binary_digests)
		final_etag_hash = m.hexdigest()
		return f'{final_etag_hash}-{len(etags)}'

	def ParseXmlRequest(this):
		if (this.xml_request_root is not None):
			return this.xml_request_root
		if (not this.request.data):
			return None
		try:
			this.xml_request_root = ET.fromstring(this.request.data)
			return this.xml_request_root
		except ET.ParseError as e:
			raise apie.OtherAPIError("InvalidXML", f"The XML you provided was not well-formed or did not validate against our published schema: {e}", 400)

	def fetch_location_request_xml(this, varName, default, fetchFrom, attempted):
		root = this.ParseXmlRequest()
		if (root is None):
			return default, False
		element = root.find(f'.//{{*}}{varName}') 
		if (element is None):
			element = root.find(varName)
		if (element is not None and element.text):
			logging.debug(f"Fetched '{varName}' from XML body with value: {element.text}")
			return element.text, True
		return default, False

	def BuildXmlResponse(this, root_tag_name, data_dict):
		def build_elements(parent, data):
			if (isinstance(data, dict)):
				for key, val in data.items():
					element = ET.SubElement(parent, key)
					build_elements(element, val)
			elif (isinstance(data, list)):
				for item in data:
					build_elements(parent, item)
			else:
				parent.text = str(data)

		ET.register_namespace('', this.s3_namespace)
		root = ET.Element(root_tag_name)
		build_elements(root, data_dict)
		this.clobberContent = False
		this.response.content.message = ET.tostring(root, encoding='unicode')
		this.response.code = 200

	def HandleError(this, s3_code, message, http_status_code, resource=None):
		error_data = {
			"Code": s3_code,
			"Message": message,
			"Resource": resource if resource else this.request.path,
			"RequestId": str(uuid.uuid4())
		}
		root = ET.Element('Error')
		for key, val in error_data.items():
			ET.SubElement(root, key).text = val
		this.clobberContent = False
		this.response.content.message = ET.tostring(root, encoding='unicode')
		this.response.code = http_status_code
		return this.ProcessResponse()