"""
Lacuna Signer Python Client Wrapper

A user-friendly wrapper for the Lacuna Signer API that provides high-level operations
for digital signatures, document management, and workflow automation.

Based on the Lacuna Signer documentation: https://docs.lacunasoftware.com/pt-br/articles/signer/index.html
"""

import os
import base64
from typing import List, Dict, Any, Optional, Union, BinaryIO
from pathlib import Path

# Import the generated client
import sys
sys.path.append('../dist')

from signer_client import (
    Configuration, ApiClient,
    DocumentsApi, FlowsApi, FoldersApi, MarksSessionsApi, 
    NotificationsApi, OrganizationsApi, UploadApi
)
from signer_client.models import (
    # Document Models
    DocumentsCreateDocumentRequest, DocumentsCreateDocumentResult,
    DocumentsDocumentModel, DocumentsDocumentListModel,
    DocumentsDocumentFileModel, DocumentsDocumentContentModel,
    DocumentsDocumentSignaturesInfoModel, DocumentsDocumentPermissionsModel,
    DocumentsDocumentTagModel, DocumentsDocumentTagData,
    DocumentsDocumentAdditionalInfoData, DocumentsCreatorModel,
    
    # Document Request Models
    DocumentsActionUrlRequest, DocumentsActionUrlResponse,
    DocumentsCancelDocumentRequest, DocumentsDocumentAddVersionRequest,
    DocumentsDocumentFlowEditRequest, DocumentsDocumentNotifiedEmailsEditRequest,
    DocumentsEnvelopeAddVersionRequest, DocumentsMoveDocumentRequest,
    DocumentsMoveDocumentBatchRequest, DocumentsPrePositionedMarkModel,
    DocumentsFlowActionPendingModel,
    
    # Document Flow Models
    DocumentFlowsDocumentFlowCreateRequest, DocumentFlowsDocumentFlowModel,
    DocumentFlowsDocumentFlowData, DocumentFlowsDocumentFlowDetailsModel,
    
    # Folder Models
    FoldersFolderCreateRequest, FoldersFolderInfoModel, FoldersFolderOrganizationModel,
    FoldersFolderDeleteRequest,
    
    # Upload Models
    UploadsUploadBytesRequest, UploadsUploadBytesModel, FileModel, UploadModel, FileUploadModel,
    
    # Flow Action Models
    FlowActionsFlowActionCreateModel, FlowActionsFlowActionModel,
    FlowActionsFlowActionEditModel, FlowActionsDocumentFlowEditResponse,
    FlowActionsApprovalModel, FlowActionsSignatureModel, FlowActionsPendingActionModel,
    FlowActionsRectifiedParticipantModel, FlowActionsSignRuleUserModel,
    FlowActionsSignRuleUserEditModel, FlowActionsXadesOptionsModel,
    
    # User Models
    UsersParticipantUserModel,
    
    # Enum Types
    DocumentStatus, DocumentTypes, FolderType, FlowActionType,
    SignatureTypes, AuthenticationTypes, PaginationOrders,
    DocumentDownloadTypes, DocumentTicketType, DocumentFilterStatus,
    DocumentQueryTypes, DocumentMarkType,
    
    # Notification Models
    NotificationsCreateFlowActionReminderRequest, NotificationsEmailListNotificationRequest,
    
    # Pagination Models
    PaginatedSearchResponseDocumentsDocumentListModel, 
    PaginatedSearchResponseFoldersFolderInfoModel,
    PaginatedSearchResponseDocumentFlowsDocumentFlowModel,
    PaginatedSearchResponseOrganizationsOrganizationUserModel,
    
    # Organization Models
    OrganizationsOrganizationUserPostRequest, OrganizationsOrganizationUserModel,
    
    # Mark Session Models
    DocumentMarkMarksSessionCreateRequest, DocumentMarkMarksSessionCreateResponse,
    DocumentMarkMarksSessionModel, DocumentMarkDocumentMarkPositionModel,
    DocumentMarkFlowActionPositionModel, DocumentMarkPrePositionedDocumentMarkModel,
    DocumentMarkUploadTicketModel,
    
    # Other Models
    BatchItemResultModel, TicketModel, SignatureSignaturesInfoRequest,
    RefusalRefusalRequest, RefusalRefusalModel, SignerModel,
    
    # Webhook Models
    WebhooksDocumentSignedModel, WebhooksDocumentApprovedModel,
    WebhooksDocumentRefusedModel, WebhooksDocumentConcludedModel,
    WebhooksDocumentCanceledModel, WebhooksDocumentExpiredModel,
    WebhooksDocumentsCreatedModel, WebhooksDocumentsDeletedModel,
    WebhooksDocumentsDeletedAction, WebhooksDocumentInformationModel,
    
    # Health Document Models
    HealthDocumentsHealthDocumentData, HealthDocumentsHealthItemModel,
    HealthDocumentsHealthProfessionalModel
)


class SignerClient:
    """
    A comprehensive client for the Lacuna Signer API that provides high-level operations
    for digital signatures and document management.
    
    The Lacuna Signer is an intelligent signature manager that allows you to collect
    different types of signatures with a fast, intuitive, and customizable system.
    
    Features:
    - Digital and electronic signatures with legal validity
    - Individual instances for each client with separate databases and storage
    - Support for various document types (contracts, proposals, medical reports, etc.)
    """
    
    def __init__(self, api_key: str, base_url: str = "https://signer-demo.lacunasoftware.com"):
        """
        Initialize the Signer client.
        
        Args:
            api_key: Your API key in the format 'your-app|xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            base_url: The base URL for the Signer API (defaults to demo environment)
        """
        self.configuration = Configuration()
        self.configuration.host = base_url
        self.configuration.api_key = {'X-Api-Key': api_key}
        self.api_client = ApiClient(configuration=self.configuration)
        
        # Initialize all API clients
        self.documents_api = DocumentsApi(self.api_client)
        self.flows_api = FlowsApi(self.api_client)
        self.folders_api = FoldersApi(self.api_client)
        self.marks_sessions_api = MarksSessionsApi(self.api_client)
        self.notifications_api = NotificationsApi(self.api_client)
        self.organizations_api = OrganizationsApi(self.api_client)
        self.upload_api = UploadApi(self.api_client)
    
    # ============================================================================
    # DOCUMENT MANAGEMENT
    # ============================================================================
    
    def create_document(self, document_request: DocumentsCreateDocumentRequest) -> DocumentsDocumentModel:
        """
        Create a new document with signature flow.
        
        Args:
            document_request: Document creation request with flow actions
            
        Returns:
            Created document details
        """
        return self.documents_api.api_documents_post(body=document_request)
    
    def get_document(self, document_id: str) -> DocumentsDocumentModel:
        """
        Get document details by ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            Document details
        """
        return self.documents_api.api_documents_id_get(document_id)
    
    def list_documents(self, 
                      status: Optional[DocumentStatus] = None,
                      folder_id: Optional[str] = None,
                      document_type: Optional[DocumentTypes] = None,
                      query: Optional[str] = None,
                      limit: int = 20,
                      offset: int = 0,
                      order: Optional[PaginationOrders] = None) -> PaginatedSearchResponseDocumentsDocumentListModel:
        """
        List documents with optional filtering.
        
        Args:
            status: Filter by document status
            folder_id: Filter by folder ID
            document_type: Filter by document type
            query: Search query
            limit: Number of items to return
            offset: Pagination offset
            order: Sort order
            
        Returns:
            Paginated list of documents
        """
        return self.documents_api.api_documents_get(
            status=status,
            folder_id=folder_id,
            document_type=document_type,
            q=query,
            limit=limit,
            offset=offset,
            order=order
        )
    
    def get_document_content(self, document_id: str) -> bytes:
        """
        Get document content as bytes.
        
        Args:
            document_id: The document ID
            
        Returns:
            Document content as bytes
        """
        return self.documents_api.api_documents_id_content_get(document_id)
    
    def get_document_content_b64(self, document_id: str) -> str:
        """
        Get document content as base64 string.
        
        Args:
            document_id: The document ID
            
        Returns:
            Document content as base64 string
        """
        return self.documents_api.api_documents_id_content_b64_get(document_id)
    
    def get_document_signatures_details(self, document_id: str) -> DocumentsDocumentSignaturesInfoModel:
        """
        Get detailed signature information for a document.
        
        Args:
            document_id: The document ID
            
        Returns:
            Document signatures details
        """
        return self.documents_api.api_documents_id_signatures_details_get(document_id)
    
    def get_document_ticket(self, document_id: str) -> TicketModel:
        """
        Get document ticket for signing.
        
        Args:
            document_id: The document ID
            
        Returns:
            Document ticket information
        """
        return self.documents_api.api_documents_id_ticket_get(document_id)
    
    def get_document_download_ticket(self, document_id: str, ticket_type: DocumentTicketType) -> TicketModel:
        """
        Get document download ticket with specified type.
        
        Args:
            document_id: The document ID
            ticket_type: The type of ticket to generate (DocumentTicketType enum)
            
        Returns:
            Document ticket information
        """
        return self.documents_api.api_documents_id_ticket_get(document_id, type=ticket_type)
    
    def delete_document(self, document_id: str) -> None:
        """
        Delete a document.
        
        Args:
            document_id: The document ID
        """
        self.documents_api.api_documents_id_delete(document_id)
    
    def move_document_to_folder(self, document_id: str, folder_id: str) -> None:
        """
        Move a document to a specific folder.
        
        Args:
            document_id: The document ID
            folder_id: The target folder ID
        """
        request = DocumentsMoveDocumentRequest(folder_id=folder_id)
        self.documents_api.api_documents_id_folder_post(document_id, body=request)
    
    def move_documents_batch_to_folder(self, document_ids: List[str], folder_id: str) -> List[BatchItemResultModel]:
        """
        Move multiple documents to a folder in batch.
        
        Args:
            document_ids: List of document IDs
            folder_id: The target folder ID
            
        Returns:
            Batch operation results
        """
        request = DocumentsMoveDocumentBatchRequest(
            documents=document_ids,
            folder_id=folder_id
        )
        return self.documents_api.api_documents_batch_folder_post(body=request)
    
    def update_document_notified_emails(self, document_id: str, emails: List[str]) -> None:
        """
        Update the emails that will be notified when document is concluded.
        
        Args:
            document_id: The document ID
            emails: List of email addresses to notify
        """
        request = DocumentsDocumentNotifiedEmailsEditRequest(emails=emails)
        self.documents_api.api_documents_id_notified_emails_put(document_id, body=request)
    
    def create_document_version(self, document_id: str, version_request: DocumentsDocumentAddVersionRequest) -> DocumentsDocumentModel:
        """
        Create a new version of a document.
        
        Args:
            document_id: The document ID
            version_request: Version creation request
            
        Returns:
            New document version details
        """
        return self.documents_api.api_documents_id_versions_post(document_id, body=version_request)
    
    def create_document_envelope_version(self, document_id: str, envelope_request: DocumentsEnvelopeAddVersionRequest) -> DocumentsDocumentModel:
        """
        Create a new envelope version of a document.
        
        Args:
            document_id: The document ID
            envelope_request: Envelope version creation request
            
        Returns:
            New document envelope version details
        """
        return self.documents_api.api_documents_id_envelope_versions_post(document_id, body=envelope_request)
    
    def get_signatures_by_key(self, key: str) -> DocumentsDocumentSignaturesInfoModel:
        """
        Get signatures by document key.
        
        Args:
            key: The document key
            
        Returns:
            Document signatures information
        """
        return self.documents_api.api_documents_keys_key_signatures_get(key)
    
    def validate_signatures(self, validation_request: SignatureSignaturesInfoRequest) -> List[SignerModel]:
        """
        Validate document signatures.
        
        Args:
            validation_request: Signature validation request
            
        Returns:
            List of signer models
        """
        return self.documents_api.api_documents_validate_signatures_post(body=validation_request)
    
    def create_action_url(self, document_id: str, action_request: DocumentsActionUrlRequest) -> DocumentsActionUrlResponse:
        """
        Create an action URL for document signing.
        
        Args:
            document_id: The document ID
            action_request: Action URL creation request
            
        Returns:
            Action URL details
        """
        return self.documents_api.api_documents_id_action_url_post(document_id, body=action_request)
    
    def cancel_document(self, document_id: str, cancellation_request: DocumentsCancelDocumentRequest) -> None:
        """
        Cancel a document.
        
        Args:
            document_id: The document ID
            cancellation_request: Cancellation request
        """
        self.documents_api.api_documents_id_cancellation_post(document_id, body=cancellation_request)
    
    def refuse_document(self, document_id: str, refusal_request: RefusalRefusalRequest) -> None:
        """
        Refuse a document.
        
        Args:
            document_id: The document ID
            refusal_request: Refusal request
        """
        self.documents_api.api_documents_id_refusal_post(document_id, body=refusal_request)
    
    def create_document_flow(self, document_id: str, flow_request: DocumentsDocumentFlowEditRequest) -> DocumentsDocumentModel:
        """
        Create a signature flow for a document.
        
        Args:
            document_id: The document ID
            flow_request: Flow creation request
            
        Returns:
            Updated document with flow
        """
        return self.documents_api.api_documents_id_flow_post(document_id, body=flow_request)
    
    # ============================================================================
    # FOLDER MANAGEMENT
    # ============================================================================
    
    def create_folder(self, folder_request: FoldersFolderCreateRequest) -> FoldersFolderInfoModel:
        """
        Create a new folder.
        
        Args:
            folder_request: Folder creation request
            
        Returns:
            Created folder details
        """
        return self.folders_api.api_folders_post(body=folder_request)
    
    def get_folder(self, folder_id: str) -> FoldersFolderInfoModel:
        """
        Get folder details by ID.
        
        Args:
            folder_id: The folder ID
            
        Returns:
            Folder details
        """
        return self.folders_api.api_folders_id_get(folder_id)
    
    def list_folders(self, 
                    query: Optional[str] = None,
                    limit: int = 20,
                    offset: int = 0,
                    order: Optional[PaginationOrders] = None,
                    parent_id: Optional[str] = None) -> PaginatedSearchResponseFoldersFolderInfoModel:
        """
        List folders with optional filtering.
        
        Args:
            query: Search query
            limit: Number of items to return
            offset: Pagination offset
            order: Sort order
            parent_id: Filter by parent folder ID
            
        Returns:
            Paginated list of folders
        """
        return self.folders_api.api_folders_get(
            q=query,
            limit=limit,
            offset=offset,
            order=order,
            filter_by_parent=parent_id is not None,
            parent_id=parent_id
        )
    
    def delete_folder(self, folder_id: str, delete_request: FoldersFolderDeleteRequest) -> None:
        """
        Delete a folder.
        
        Args:
            folder_id: The folder ID
            delete_request: Folder deletion request
        """
        self.folders_api.api_folders_id_delete_post(folder_id, body=delete_request)
    
    # ============================================================================
    # SIGNATURE FLOW MANAGEMENT
    # ============================================================================
    
    def create_signature_flow(self, 
                            document_id: str,
                            signers: List[Dict],
                            title: Optional[str] = None,
                            description: Optional[str] = None,
                            expires_at: Optional[str] = None) -> DocumentFlowsDocumentFlowModel:
        """
        Create a signature flow for a document.
        
        Args:
            document_id: The document to be signed
            signers: List of signer dictionaries with keys:
                     - name: Signer's name
                     - email: Signer's email
                     - identifier: Signer's identifier (Brazilian ID)
                     - signature_type: Type of signature (digital, electronic, etc.)
            title: Optional flow title
            description: Optional flow description
            expires_at: Optional expiration date (ISO format)
            
        Returns:
            Created flow model
        """
        # Create flow actions for each signer
        flow_actions = []
        for i, signer in enumerate(signers):
            action = FlowActionsFlowActionCreateModel(
                type=FlowActionType.SIGNER,
                step=i + 1,
                user=UsersParticipantUserModel(
                    name=signer['name'],
                    email=signer['email'],
                    identifier=signer.get('identifier')
                ),
                
                authentication_type=signer.get('authentication_type', AuthenticationTypes.EMAIL)
            )
            flow_actions.append(action)
        
        # Create flow request
        flow_request = DocumentFlowsDocumentFlowCreateRequest(
            title=title,
            description=description,
            expires_at=expires_at,
            flow_actions=flow_actions
        )
        
        return self.flows_api.api_document_flows_post(body=flow_request)
    
    def get_signature_flow(self, flow_id: str) -> DocumentFlowsDocumentFlowModel:
        """
        Get signature flow details.
        
        Args:
            flow_id: The flow ID
            
        Returns:
            Flow model with all details
        """
        return self.flows_api.api_document_flows_id_get(flow_id)
    
    def list_signature_flows(self, limit: int = 20, offset: int = 0) -> List[DocumentFlowsDocumentFlowModel]:
        """
        List signature flows.
        
        Args:
            limit: Number of flows to return
            offset: Pagination offset
            
        Returns:
            List of flow models
        """
        response = self.flows_api.api_document_flows_get(limit=limit, offset=offset)
        return response.items if hasattr(response, 'items') else response
    
    def cancel_signature_flow(self, flow_id: str, reason: Optional[str] = None) -> None:
        """
        Cancel a signature flow.
        
        Args:
            flow_id: The flow ID to cancel
            reason: Optional cancellation reason
        """
        self.flows_api.api_document_flows_id_delete(flow_id)
    
    def update_signature_flow(self, flow_id: str, flow_request: DocumentFlowsDocumentFlowCreateRequest) -> DocumentFlowsDocumentFlowModel:
        """
        Update a signature flow.
        
        Args:
            flow_id: The flow ID
            flow_request: Flow update request
            
        Returns:
            Updated flow details
        """
        return self.flows_api.api_document_flows_id_put(flow_id, body=flow_request)
    
    def delete_signature_flow(self, flow_id: str) -> None:
        """
        Delete a signature flow.
        
        Args:
            flow_id: The flow ID
        """
        return self.flows_api.api_document_flows_id_delete(flow_id)
    
    # ============================================================================
    # FILE UPLOAD
    # ============================================================================
    
    def upload_file(self, file_path: str) -> FileModel:
        """
        Upload a file using multipart/form-data.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            Uploaded file details
        """
        with open(file_path, 'rb') as file:
            return self.upload_api.api_uploads_post(file=file)
    
    def upload_file_bytes(self, file_bytes: bytes) -> UploadModel:
        """
        Upload file bytes to the server.
        
        Args:
            file_name: Name of the file
            file_bytes: File content as bytes
            content_type: MIME type of the file (optional)
            
        Returns:
            Upload model with file information
        """
        import base64
        
        # Encode bytes as base64
        base64_bytes = base64.b64encode(file_bytes).decode('utf-8')
        
        request = UploadsUploadBytesRequest(
            bytes=base64_bytes
        )
        
        return self.upload_api.api_uploads_bytes_post(body=request)
    
    # ============================================================================
    # NOTIFICATIONS
    # ============================================================================
    
    def send_reminder(self, flow_action_id: str, message: Optional[str] = None) -> None:
        """
        Send a reminder to a signer.
        
        Args:
            flow_action_id: The flow action ID (signer's pending action)
            message: Optional custom reminder message
        """
        request = {
            'flow_action_id': flow_action_id
        }
        if message:
            request['message'] = message
        
        self.notifications_api.api_notifications_flow_action_reminder_post(body=request)
    
    def notify_pending_users(self, email_list: List[str]) -> None:
        """
        Send notifications to users with pending actions.
        
        Args:
            email_list: List of email addresses to notify
        """
        request = {
            'email_list': email_list
        }
        
        self.notifications_api.api_users_notify_pending_post(body=request)
    
    # ============================================================================
    # ORGANIZATION MANAGEMENT
    # ============================================================================
    
    def get_organization_info(self):
        """
        Get current organization information.
        
        Returns:
            Organization information model
        """
        return self.organizations_api.api_organizations_get()
    
    def list_organization_users(self, 
                              query: Optional[str] = None,
                              limit: int = 20,
                              offset: int = 0,
                              order: Optional[PaginationOrders] = None) -> PaginatedSearchResponseOrganizationsOrganizationUserModel:
        """
        List organization users.
        
        Args:
            query: Search query
            limit: Number of items to return
            offset: Pagination offset
            order: Sort order
            
        Returns:
            Paginated list of organization users
        """
        return self.organizations_api.api_organizations_users_get(
            q=query,
            limit=limit,
            offset=offset,
            order=order
        )
    
    def add_organization_user(self, user_request: OrganizationsOrganizationUserPostRequest) -> OrganizationsOrganizationUserModel:
        """
        Add a user to the organization.
        
        Args:
            user_request: User creation request
            
        Returns:
            Created user details
        """
        return self.organizations_api.api_organizations_users_post(body=user_request)
    
    def remove_organization_user(self, user_id: str) -> None:
        """
        Remove a user from the organization.
        
        Args:
            user_id: The user ID
        """
        self.organizations_api.api_organizations_users_user_id_delete(user_id)
    
    # ============================================================================
    # MARKS SESSIONS
    # ============================================================================
    
    def create_marks_session(self, session_request: DocumentMarkMarksSessionCreateRequest) -> DocumentMarkMarksSessionCreateResponse:
        """
        Create a mark positioning session.
        
        Args:
            session_request: Session creation request
            
        Returns:
            Session creation response
        """
        return self.marks_sessions_api.api_marks_sessions_post(body=session_request)
    
    def create_marks_session_from_document(self, document_request: DocumentsCreateDocumentRequest) -> DocumentMarkMarksSessionCreateResponse:
        """
        Create a mark positioning session from a document request.
        
        Args:
            document_request: Document creation request
            
        Returns:
            Session creation response
        """
        return self.marks_sessions_api.api_marks_sessions_documents_post(body=document_request)
    
    def get_marks_session(self, session_id: str) -> DocumentMarkMarksSessionModel:
        """
        Get marks session details.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session details
        """
        return self.marks_sessions_api.api_marks_sessions_id_get(session_id)
    
    # ============================================================================
    # HIGH-LEVEL OPERATIONS
    # ============================================================================
    
    def sign_document_simple(self, request: DocumentsCreateDocumentRequest) -> DocumentsDocumentModel:
        """
        Create a document and signature flow in one operation.
        
        Args:
            request: Document creation request with files and flow actions
            
        Returns:
            Created document details
        """
        return self.documents_api.api_documents_post(body=request)
    
    def create_document_with_signer(self, 
                                  file_upload: FileUploadModel,
                                  title: str,
                                  signer: UsersParticipantUserModel,
                                  flow_action: FlowActionsFlowActionCreateModel,
                                  folder_id: Optional[str] = None) -> DocumentsDocumentModel:
        """
        Create a document with a signature flow using model objects.
        
        Args:
            file_upload: FileUploadModel with file information
            title: Document title
            signer: UsersParticipantUserModel with signer information
            flow_action: FlowActionsFlowActionCreateModel with flow action details
            folder_id: Optional folder ID to store the document
            
        Returns:
            Created document details
        """
        # Create document request
        document_request = DocumentsCreateDocumentRequest(
            files=[file_upload],
            flow_actions=[flow_action],
            folder_id=folder_id
        )
        
        return self.documents_api.api_documents_post(body=document_request)
    
    def get_document_status(self, document_id: str) -> str:
        """
        Get the current status of a document.
        
        Args:
            document_id: The document ID
            
        Returns:
            Document status
        """
        document = self.get_document(document_id)
        return document.status if document.status else "Unknown"
    
    def get_signing_url(self, document_id: str, signer_email: str) -> str:
        """
        Get the signing URL for a specific signer.
        
        Args:
            document_id: The document ID
            signer_email: Email of the signer
            
        Returns:
            Signing URL
        """
        action_request = DocumentsActionUrlRequest(
            email_address=signer_email
        )
        action_url = self.create_action_url(document_id, action_request)
        return action_url.url
    
    def download_signed_document(self, document_id: str, output_path: str) -> None:
        """
        Download a signed document to a local file.
        
        Args:
            document_id: The document ID
            output_path: Path where to save the file
        """
        content = self.get_document_content(document_id)
        with open(output_path, 'wb') as f:
            f.write(content)
    
    def get_document_summary(self, document_id: str) -> Dict[str, Any]:
        """
        Get a summary of document information.
        
        Args:
            document_id: The document ID
            
        Returns:
            Document summary dictionary
        """
        document = self.get_document(document_id)
        signatures = self.get_document_signatures_details(document_id)
        
        return {
            'id': document.id,
            'title': document.title,
            'status': document.status.value if document.status else None,
            'created_at': document.created_at,
            'updated_at': document.updated_at,
            'signature_count': len(signatures.signatures) if signatures.signatures else 0,
            'is_concluded': document.is_concluded,
            'folder_id': document.folder_id
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def close(self):
        """Close the API client and clean up resources."""
        if hasattr(self.api_client, 'close'):
            self.api_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience function for quick setup
def create_signer_client(api_key: str, base_url: str) -> SignerClient:
    """
    Create a SignerClient instance with the given API key.
    
    Args:
        api_key: Your API key
        base_url: Optional base URL (defaults to demo environment)
        
    Returns:
        Configured SignerClient instance
    """
    return SignerClient(api_key, base_url) 