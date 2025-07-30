import logging
import hmac
import hashlib
import re
import eons
import apie

# Implements S3-compliant AWS Signature Version 4 authentication.
# This Functor is called by the APIE framework for each incoming request
# to verify its integrity and authenticity before passing it to an endpoint.
class S3Auth(apie.Authenticator):
	def __init__(this, name="S3 Authenticator"):
		super().__init__(name)

	# --- Helper methods for building the canonical request ---
	
	def GetCanonicalUri(this, request):
		return request.path

	def GetCanonicalQuerystring(this, request):
		# The query string must be sorted by key.
		params = sorted(request.args.items())
		return '&'.join([f"{k}={v}" for k, v in params])

	def GetCanonicalHeaders(this, request):
		headers = {k.lower(): v.strip() for k, v in request.headers.items() if k.lower().startswith('x-amz-') or k.lower() == 'host'}
		sorted_headers = sorted(headers.items())
		return '\n'.join([f"{k}:{v}" for k, v in sorted_headers]) + '\n'

	def GetSignedHeaders(this, request):
		headers = [k.lower() for k in request.headers.keys() if k.lower().startswith('x-amz-') or k.lower() == 'host']
		return ';'.join(sorted(headers))

	def GetPayloadHash(this, request):
		# The payload hash is the SHA256 hash of the request body.
		payload = request.data or b''
		return hashlib.sha256(payload).hexdigest()

	def GetCredentialScope(this, date, region, service):
		return f"{date}/{region}/{service}/aws4_request"

	# --- Cryptographic signing key derivation ---
	
	def GetSigningKey(this, secret_key, date, region, service):
		kDate = hmac.new(f"AWS4{secret_key}".encode('utf-8'), date.encode('utf-8'), hashlib.sha256).digest()
		kRegion = hmac.new(kDate, region.encode('utf-8'), hashlib.sha256).digest()
		kService = hmac.new(kRegion, service.encode('utf-8'), hashlib.sha256).digest()
		kSigning = hmac.new(kService, b"aws4_request", hashlib.sha256).digest()
		return kSigning

	# The primary authentication method called by APIE.
	def Authenticate(this):
		auth_header = this.request.headers.get('Authorization')
		if (not auth_header or not auth_header.startswith('AWS4-HMAC-SHA256')):
			logging.debug("Missing or invalid Authorization header.")
			return False

		# --- Use a robust regex to parse the Authorization header ---
		auth_pattern = re.compile(
			r'AWS4-HMAC-SHA256 Credential=([^/]+)/([^/]+)/([^/]+)/([^,]+), SignedHeaders=([^,]+), Signature=(.+)'
		)
		match = auth_pattern.match(auth_header.split(' ', 1)[1])
		if (not match):
			logging.debug("Could not parse the Authorization header.")
			return False

		access_key_id, request_date, region, service, signed_headers, client_signature = match.groups()

		if (service != 's3'):
			logging.debug(f"Unsupported service in credential scope: {service}")
			return False

		# Fetch the secret key from the executor's config.
		# This assumes secrets are stored with a key like 'AKIA..._secret_key'.
		secret_access_key = this.executor.Fetch(f"{access_key_id}_secret_key")
		if (not secret_access_key):
			logging.debug(f"No secret key found for access key: {access_key_id}")
			return False

		# --- Create the Canonical Request ---
		http_method = this.request.method
		canonical_uri = this.GetCanonicalUri(this.request)
		canonical_querystring = this.GetCanonicalQuerystring(this.request)
		canonical_headers = this.GetCanonicalHeaders(this.request)
		payload_hash = this.GetPayloadHash(this.request)

		canonical_request = f"{http_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
		logging.debug(f"Canonical Request String:\n{canonical_request}")

		# --- Create the String to Sign ---
		algorithm = 'AWS4-HMAC-SHA256'
		amz_date = this.request.headers.get('x-amz-date')
		if (not amz_date):
			logging.debug("Request missing required x-amz-date header.")
			return False

		credential_scope = this.GetCredentialScope(request_date, region, service)
		hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

		string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
		logging.debug(f"String to Sign:\n{string_to_sign}")

		# --- Calculate our version of the signature ---
		signing_key = this.GetSigningKey(secret_access_key, request_date, region, service)
		calculated_signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

		# --- Compare our signature with the one from the client ---
		logging.debug(f"Client Signature: {client_signature}")
		logging.debug(f"Calculated Signature: {calculated_signature}")
		
		# Use hmac.compare_digest for secure, constant-time comparison.
		return hmac.compare_digest(client_signature, calculated_signature)


	def Unauthorized(this, path):
		# This method is called by the APIE framework if Authenticate() returns False.
		# It should return the S3 error code and HTTP status.
		return "SignatureDoesNotMatch", 403