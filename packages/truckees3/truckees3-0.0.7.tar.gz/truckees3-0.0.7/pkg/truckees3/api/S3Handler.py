import logging
import apie

class S3Handler(apie.Endpoint):
	def __init__(this, name="S3 Handler"):
		super().__init__(name)

	def Call(this):
		# --- Parse Path ---
		# This logic correctly handles requests to the root (e.g., ListBuckets)
		# and separates the bucket from the object key for all other requests.
		path_parts = this.request.path.strip('/').split('/', 1)
		bucket = path_parts[0] if path_parts and path_parts[0] else None
		key = path_parts[1] if len(path_parts) > 1 else None
		
		# --- Default Route ---
		this.next = []

		# --- Cache request properties for cleaner access ---
		method = this.request.method
		args = this.request.args
		headers = this.request.headers

		# --- S3 Routing Logic ---
		# This logic inspects the method, path, and query arguments to dispatch
		# the request to the correct S3 API implementation.

		if (method == 'GET'):
			if (bucket is None):
				# GET / -> List all buckets
				this.next = ['list_buckets']
			elif ('versions' in args):
				this.next = ['list_object_versions']
			elif ('versioning' in args):
				this.next = ['get_bucket_versioning']
			elif ('uploadId' in args):
				this.next = ['list_parts']
			elif (key is not None):
				this.next = ['get_object']
			else:
				# GET on a bucket path with no other specifiers -> List objects
				this.next = ['list_objects']

		elif (method == 'PUT'):
			if ('uploadId' in args and 'partNumber' in args):
				if ('x-amz-copy-source' in headers):
					this.next = ['upload_part_copy']
				else:
					this.next = ['upload_part']
			elif ('versioning' in args):
				this.next = ['put_bucket_versioning']
			elif (key is not None):
				if ('x-amz-copy-source' in headers):
					this.next = ['copy_object']
				else:
					this.next = ['put_object']
			else:
				# PUT on a bucket path -> Create bucket
				this.next = ['create_bucket']

		elif (method == 'POST'):
			if ('uploads' in args):
				this.next = ['create_multipart_upload']
			elif ('delete' in args):
				this.next = ['delete_multiple_objects']
			elif ('uploadId' in args and key is not None):
				this.next = ['complete_multipart_upload']

		elif (method == 'DELETE'):
			if ('uploadId' in args and key is not None):
				this.next = ['abort_multipart_upload']
			elif (key is not None):
				this.next = ['delete_object']
			else:
				this.next = ['delete_bucket']

		elif (method == 'HEAD'):
			if (key is not None):
				this.next = ['head_object']
			else:
				this.next = ['head_bucket']

		# --- Dispatch or Error ---
		if (not this.next):
			logging.error(f"Could not find a valid S3 route for {method} {this.request.path} with args {args}")
			raise apie.OtherAPIError("InvalidRequest", "The resource-specific request header or query parameter is not supported.", 400)

		logging.info(f"Routing {method} {this.request.path} to endpoint: {this.next[0]}")
		
		# Pass the parsed bucket and key to the next endpoint in the chain.
		return this.CallNext(bucket_name=bucket, object_key=key)