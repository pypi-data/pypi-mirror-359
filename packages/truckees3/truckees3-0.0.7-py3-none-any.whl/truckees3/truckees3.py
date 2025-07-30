import logging
from pathlib import Path
import eons
import apie
from libtruckeefs import RiverFS
import os
import uuid
from libtruckeefs import *
from eons import Functor

######## START CONTENT ########

# Manages S3 object versioning operations as a self-contained, consumable Functor.
# Provides a suite of public methods for object manipulation and status checks.
class VersionManager(eons.Functor):
	def __init__(this, name="Version Manager"):
		super().__init__(name)

		# -- Argument Definitions --
		# These arguments are expected to be in snake_case.
		this.arg.kw.required.append('bucket_name')
		this.arg.kw.optional['versions_dir_name'] = ".versions"
		this.arg.kw.optional['xattr_version_id'] = "user.s3.versionId"
		this.arg.kw.optional['xattr_delete_marker'] = "user.s3.deleteMarker"
		this.arg.kw.optional['xattr_versioning_status'] = "user.s3.versioning"
		this.arg.kw.optional['object_key'] = None
		this.arg.kw.optional['version_id'] = None
		this.arg.kw.optional['data'] = None
		this.arg.kw.optional['etag'] = None
		this.arg.kw.optional['status'] = None # 'Enabled' or 'Suspended'

	# Constructs the path to the hidden versions directory.
	def GetArchiveDirPath(this):
		return os.path.join(this.bucket_name, this.versions_dir_name)

	# Constructs the path for a specific archived historical version.
	def GetArchivedObjectPath(this, objectKey, versionId):
		return os.path.join(this.GetArchiveDirPath(), f"{objectKey}.{versionId}")

	# Writes an object, archiving the previous version if it exists.
	# Returns the version_id of the newly created object version.
	async def PutObject(this):
		objectPath = os.path.join(this.bucket_name, this.object_key)
		await this.executor.Async(
			Directory.From(this.executor, this.GetArchiveDirPath(), createIfNotExists=True)
		)

		try:
			currentObject = await this.executor.Async(Inode.From(this.executor, objectPath))
			currentVersionId = await this.executor.Async(currentObject.GetXAttr(this.xattr_version_id))
			if currentVersionId:
				archivePath = this.GetArchivedObjectPath(this.object_key, currentVersionId)
				await this.executor.Async(currentObject.Move(archivePath))
		except FileNotFoundError:
			pass # Object is new, no need to archive.

		newObject = await this.executor.Async(File.From(this.executor, objectPath, createIfNotExists=True))
		await this.executor.Async(newObject.Write(0, this.data))
		newVersionId = str(uuid.uuid4())
		await this.executor.Async(newObject.SetXAttr(this.xattr_version_id, newVersionId))
		if (this.etag):
			await this.executor.Async(newObject.SetXAttr('user.s3.etag', this.etag))

		return newVersionId

	# "Deletes" an object by creating a delete marker.
	# Returns the version_id of the new delete marker.
	async def DeleteObject(this):
		# Create an empty placeholder file which archives the previous version.
		await this.PutObject() 

		objectPath = os.path.join(this.bucket_name, this.object_key)
		deleteMarker = await this.executor.Async(File.From(this.executor, objectPath))

		# Set the delete marker attribute on this new empty version.
		markerVersionId = str(uuid.uuid4())
		await this.executor.Async(deleteMarker.SetXAttr(this.xattr_version_id, markerVersionId))
		await this.executor.Async(deleteMarker.SetXAttr(this.xattr_delete_marker, "true"))
		return markerVersionId

	# Retrieves the File Inode of the specified object at the given version or the latest.
	# Returns the File object if it exists, or None if it's a delete marker or not found.
	async def GetObject(this):
		objectPath = ""
		if this.version_id:
			objectPath = this.GetArchivedObjectPath(this.object_key, this.version_id)
		else:
			objectPath = os.path.join(this.bucket_name, this.object_key)

		try:
			objectFile = await this.executor.Async(File.From(this.executor, objectPath))
			isDeleteMarker = await this.executor.Async(objectFile.GetXAttr(this.xattr_delete_marker))
			if isDeleteMarker == "true":
				return None

			return objectFile
		except FileNotFoundError:
			return None

	# Retrieves a specific version of an object, or the latest.
	# Returns file content as bytes, or None if it's a delete marker or not found.
	async def GetObjectData(this):
		ret = await this.GetObject()
		if ret is None:
			return None
		return await ret.Read()

	# Sets the versioning status ('Enabled'/'Suspended') on a bucket.
	async def SetVersioningStatus(this):
		bucketDir = await this.executor.Async(Directory.From(this.executor, this.bucket_name))
		await this.executor.Async(bucketDir.SetXAttr(this.xattr_versioning_status, this.status))
		logging.info(f"Set versioning status for {this.bucket_name} to {this.status}")

	# Gets the versioning status from a bucket.
	async def GetVersioningStatus(this):
		bucketDir = await this.executor.Async(Directory.From(this.executor, this.bucket_name))
		status = await this.executor.Async(bucketDir.GetXAttr(this.xattr_versioning_status))
		return status or 'Suspended' # Default to Suspended if not set.

class MultipartManager(Functor):
	def __init__(this, name="Multipart Manager"):
		super().__init__(name)

		this.arg.kw.required.append('bucket_name')
		this.arg.kw.optional['temp_dir_name'] = ".tmp_uploads"
		this.arg.kw.optional['object_key'] = None
		this.arg.kw.optional['upload_id'] = None
		this.arg.kw.optional['part_number'] = None
		this.arg.kw.optional['parts'] = None
		this.arg.kw.optional['data'] = None
		this.arg.kw.optional['etag'] = None

	def GetUploadDirPath(this, uploadId):
		return os.path.join(this.bucket_name, this.temp_dir_name, uploadId)

	async def CreateUpload(this):
		uploadId = str(uuid.uuid4())
		uploadDirPath = this.GetUploadDirPath(uploadId)
		await this.executor.Async(
			Directory.From(this.executor, uploadDirPath, createIfNotExists=True)
		)
		logging.info(f"Created temporary upload directory: {uploadDirPath}")
		return uploadId

	async def UploadPart(this):
		partPath = os.path.join(this.GetUploadDirPath(this.upload_id), str(this.part_number))
		partFile = await this.executor.Async(
			File.From(this.executor, partPath, createIfNotExists=True)
		)
		await this.executor.Async(partFile.Write(0, this.data))
		if (this.etag):
			await this.executor.Async(partFile.SetXAttr('user.s3.etag', this.etag))
		logging.info(f"Wrote part {this.part_number} to {partPath}")

	async def CompleteUpload(this):
		finalObjectPath = os.path.join(this.bucket_name, this.object_key)
		uploadDirPath = this.GetUploadDirPath(this.upload_id)
		
		tempObjectPath = os.path.join(uploadDirPath, f"__temp__{uuid.uuid4()}")
		tempFile = await this.executor.Async(
			File.From(this.executor, tempObjectPath, createIfNotExists=True)
		)

		currentOffset = 0
		this.parts.sort(key=lambda p: p['PartNumber'])
		
		for partInfo in this.parts:
			try:
				partPath = os.path.join(uploadDirPath, str(partInfo['PartNumber']))
				partFile = await this.executor.Async(File.From(this.executor, partPath))
				partAttr = await this.executor.Async(partFile.GetAttr())
				data = await this.executor.Async(partFile.Read(0, partAttr['size']))
				await this.executor.Async(tempFile.Write(currentOffset, data))
				currentOffset += len(data)
			except Exception as e:
				logging.error(f"Failed to assemble part number {partInfo['PartNumber']} for {this.object_key}: {e}")
				await this.executor.Async(tempFile.Unlink())
				error_details = {
					"Code": "InvalidPart",
					"Message": "One or more of the specified parts could not be found.",
					"PartNumber": partInfo['PartNumber']
				}
				return (False, error_details)

		finalFile = await this.executor.Async(
			tempFile.Move(finalObjectPath)
		)

		await this.CleanupTempDir(uploadDirPath)
		logging.info(f"Completed multipart upload for {finalObjectPath}")
		return (True, finalFile)

	async def AbortUpload(this):
		uploadDirPath = this.GetUploadDirPath(this.upload_id)
		await this.CleanupTempDir(uploadDirPath)
		logging.info(f"Aborted upload and deleted: {uploadDirPath}")
		
	async def ListParts(this):
		uploadDirPath = this.GetUploadDirPath(this.upload_id)
		uploadDir = await this.executor.Async(Directory.From(this.executor, uploadDirPath))
		children = await this.executor.Async(uploadDir.List())
		
		partsList = []
		for childInode in children:
			etag = await childInode.GetXAttr('user.s3.etag')
			attrs = await childInode.GetAttr()
			partsList.append({
				'PartNumber': int(childInode.name),
				'attrs': attrs,
				'ETag': etag
			})
		return sorted(partsList, key=lambda p: p['PartNumber'])

	async def CleanupTempDir(this, dirPath):
		logging.info(f"Cleaning up temporary directory: {dirPath}")
		try:
			uploadDir = await this.executor.Async(Directory.From(this.executor, dirPath))
			# First, unlink all the individual part files within the directory. 
			children = await this.executor.Async(uploadDir.List()) # 
			for child in children:
				await this.executor.Async(child.Unlink()) # 
			
			# Now that the directory is empty, unlink the directory itself. 
			await this.executor.Async(uploadDir.Unlink()) # 
		except Exception as e:
			logging.warning(f"Could not fully clean up temporary directory {dirPath}: {e}")

# The TRUCKEES3 Executor combines the filesystem logic from RiverFS with the
# web server logic from APIE to create a fully-functional S3-compatible gateway.
class TRUCKEES3(RiverFS, apie.APIE):

	def __init__(this, name="Truckee S3 Gateway"):
		# To handle the multiple inheritance, we explicitly call the
		# initializers for both parent classes. This ensures all configurations
		# from both frameworks are properly set up.
		RiverFS.__init__(this, name)
		apie.APIE.__init__(this, name)

		# --- Override Defaults for S3 Functionality ---
		this.defaultConfigFile = "truckees3.json"
		this.defaultPackageType = "s3"

		# Set the S3-specific authenticator and the main request router.
		this.arg.kw.optional['authenticator'] = "S3Auth"
		this.arg.kw.optional['preprocessor'] = "S3Handler"

		# --- Manager Instantiation ---
		# Instantiate and store the versioning and multipart managers directly
		# on the executor. Endpoints will access these shared instances via
		# 'this.executor.manager...'.
		this.manager = eons.util.DotDict()
		this.manager.version = VersionManager()
		this.manager.multipart = MultipartManager()


	def RegisterIncludedClasses(this):
		# Explicitly register the necessary classes from both parent frameworks.
		RiverFS.RegisterIncludedClasses(this)
		apie.APIE.RegisterIncludedClasses(this)

		# Register all S3-specific endpoints and authenticators so they are
		# available to the APIE framework.
		inc_path = Path(__file__).resolve().parent.parent.joinpath("inc")
		this.RegisterAllClassesInDirectory(str(inc_path))
		this.RegisterAllClassesInDirectory(str(inc_path.joinpath("api")))


	def Function(this):
		# The Function method is the main entry point for an eons.Executor.
		# Here, we combine the startup sequences of the backend and frontend.

		# 1. Initialize the RiverFS backend (DB, Tahoe, Daemons).
		#    This method is non-blocking as it starts the event loop in a
		#    separate thread before returning.
		RiverFS.Function(this)
		logging.info("RiverFS backend initialized successfully.")

		# 2. Initialize and start the APIE frontend web server.
		#    This method is blocking and will run indefinitely, serving API
		#    requests which interact with the now-running RiverFS backend.
		logging.info("Starting APIE frontend for S3 gateway.")
		apie.APIE.Function(this)
