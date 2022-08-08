
#   Copyright (c) 2022 Asif Arman Rahman
#   Licensed under MIT (https://github.com/AsifArmanRahman/firebase/blob/main/LICENSE)

# --------------------------------------------------------------------------------------


"""
A simple python wrapper for Google's `Firebase Cloud Firestore REST API`_

.. _Firebase Cloud Firestore REST API:
	https://firebase.google.com/docs/firestore/reference/rest
"""

from math import ceil
from proto.message import Message
from google.cloud.firestore import Client
from google.cloud.firestore_v1._helpers import *

from ._utils import _from_datastore
from firebase._exception import raise_detailed_error


class Firestore:
	""" Firebase Firestore Service

	:type api_key: str
	:param api_key: ``apiKey`` from Firebase configuration

	:type credentials: :class:`~google.oauth2.service_account.Credentials`
	:param credentials: Service Account Credentials

	:type project_id: str
	:param project_id: ``projectId`` from Firebase configuration

	:type requests: :class:`~requests.Session`
	:param requests: Session to make HTTP requests
	"""

	def __init__(self, api_key, credentials, project_id, requests):
		""" Constructor method """

		self._api_key = api_key
		self._credentials = credentials
		self._project_id = project_id
		self._requests = requests

	def collection(self, collection_id):
		""" Get reference to a collection in a Firestore database.


		:type collection_id: str
		:param collection_id: An ID of collection in firestore.


		:return: Reference to a collection.
		:rtype: Collection
		"""

		return Collection([collection_id], api_key=self._api_key, credentials=self._credentials, project_id=self._project_id, requests=self._requests)


class Collection:
	""" A reference to a collection in a Firestore database.

	:type collection_path: list
	:param collection_path: Collective form of strings to create a
		Collection.

	:type api_key: str
	:param api_key: ``apiKey`` from Firebase configuration

	:type credentials: :class:`~google.oauth2.service_account.Credentials`
	:param credentials: Service Account Credentials

	:type project_id: str
	:param project_id: ``projectId`` from Firebase configuration

	:type requests: :class:`~requests.Session`
	:param requests: Session to make HTTP requests
	"""

	def __init__(self, collection_path, api_key, credentials, project_id, requests):
		""" Constructor method """

		self._path = collection_path

		self._api_key = api_key
		self._credentials = credentials
		self._project_id = project_id
		self._requests = requests

	def document(self, document_id):
		""" A reference to a document in a collection.


		:type document_id: str
		:param document_id: An ID of document inside a collection.


		:return: Reference to a document.
		:rtype: Document
		"""

		self._path.append(document_id)
		return Document(self._path, api_key=self._api_key, credentials=self._credentials, project_id=self._project_id, requests=self._requests)


class Document:
	""" A reference to a document in a Firestore database.

	:type document_path: list
	:param document_path: Collective form of strings to create a
		Document.

	:type api_key: str
	:param api_key: ``apiKey`` from Firebase configuration

	:type credentials: :class:`~google.oauth2.service_account.Credentials`
	:param credentials: Service Account Credentials

	:type project_id: str
	:param project_id: ``projectId`` from Firebase configuration

	:type requests: :class:`~requests.Session`
	:param requests: Session to make HTTP requests
	"""

	def __init__(self, document_path, api_key, credentials, project_id, requests):
		""" Constructor method """

		self._path = document_path

		self._api_key = api_key
		self._credentials = credentials
		self._project_id = project_id
		self._requests = requests

		self._base_path = f"projects/{self._project_id}/databases/(default)/documents"
		self._base_url = f"https://firestore.googleapis.com/v1/{self._base_path}"

		if self._credentials:
			self.__datastore = Client(credentials=self._credentials, project=self._project_id)

	def collection(self, collection_id):
		""" A reference to a collection in a Firestore database.


		:type collection_id: str
		:param collection_id: An ID of collection in firestore.


		:return: Reference to a collection.
		:rtype: Collection
		"""

		self._path.append(collection_id)
		return Collection(self._path, api_key=self._api_key, credentials=self._credentials, project_id=self._project_id, requests=self._requests)

	def delete(self, token=None):
		""" Deletes the current document from firestore.

		| For more details:
		| |delete_documents|_

		.. |delete_documents| replace::
			Firebase Documentation | Delete data from Cloud
			Firestore | Delete documents

		.. _delete_documents:
			https://firebase.google.com/docs/firestore/manage-data/delete-data#delete_documents

		:type token: str
		:param token: (Optional) Firebase Auth User ID Token, defaults
			to :data:`None`.
		"""

		path = self._path.copy()
		self._path.clear()

		if self._credentials:
			db_ref = _build_db(self.__datastore, path)

			db_ref.delete()

		else:
			req_ref = f"{self._base_url}/{'/'.join(path)}?key={self._api_key}"

			if token:
				headers = {"Authorization": "Firebase " + token}
				response = self._requests.delete(req_ref, headers=headers)

			else:
				response = self._requests.delete(req_ref)

			raise_detailed_error(response)

	def get(self, field_paths=None, token=None):
		""" Read data from a document in firestore.


		:type field_paths: list
		:param field_paths: (Optional) A list of field paths
			(``.``-delimited list of field names) to filter data, and
			return the filtered values only, defaults
			to :data:`None`.

		:type token: str
		:param token: (Optional) Firebase Auth User ID Token, defaults
			to :data:`None`.


		:return: The whole data stored in the document unless filtered
			to retrieve specific fields.
		:rtype: dict
		"""

		path = self._path.copy()
		self._path.clear()

		if self._credentials:
			db_ref = _build_db(self.__datastore, path)

			result = db_ref.get(field_paths=field_paths)

			return result.to_dict()

		else:

			mask = ''

			if field_paths:
				for field_path in field_paths:
					mask = f"{mask}mask.fieldPaths={field_path}&"

			req_ref = f"{self._base_url}/{'/'.join(path)}?{mask}key={self._api_key}"

			if token:
				headers = {"Authorization": "Firebase " + token}
				response = self._requests.get(req_ref, headers=headers)

			else:
				response = self._requests.get(req_ref)

			raise_detailed_error(response)

			return _from_datastore(response.json())

	def set(self, data, token=None):
		""" Add data to a document in firestore.

		| For more details:
		| |set_a_document|_

		.. |set_a_document| replace::
			Firebase Documentation | Add data to Cloud Firestore | Set
			a document

		.. _set_a_document:
			https://firebase.google.com/docs/firestore/manage-data/add-data#set_a_document


		:type data: dict
		:param data: Data to be stored in firestore.

		:type token: str
		:param token: (Optional) Firebase Auth User ID Token, defaults
			to :data:`None`.
		"""

		path = self._path.copy()
		self._path.clear()

		if self._credentials:
			db_ref = _build_db(self.__datastore, path)

			db_ref.set(data)

		else:

			req_ref = f"{self._base_url}:commit?key={self._api_key}"

			body = {
				"writes": [
					Message.to_dict(pbs_for_set_no_merge(f"{self._base_path}/{'/'.join(path)}", data)[0])
					]
			}

			if token:
				headers = {"Authorization": "Firebase " + token}
				response = self._requests.post(req_ref, headers=headers, json=body)

			else:
				response = self._requests.post(req_ref, json=body)

			raise_detailed_error(response)


def _build_db(db, path):
	""" Returns a reference to Collection/Document with admin
	credentials.


	:type db: :class:`~google.cloud.firestore.Client`
	:param db: Reference to Firestore Client.

	:type path: list
	:param path: Collective form of strings to create a document.


	:return: Reference to collection/document to perform CRUD 
		operations.
	:rtype: :class:`~google.cloud.firestore_v1.document.CollectionReference`
		or :class:`~google.cloud.firestore_v1.document.DocumentReference`
	"""

	n = ceil(len(path) / 2)

	for _ in range(n):
		db = db.collection(path.pop(0))

		if len(path) > 0:
			db = db.document(path.pop(0))

	return db