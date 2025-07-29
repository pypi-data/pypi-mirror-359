"""
Bulk operation mixins for DRF ViewSets.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

try:
    from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
except ImportError:
    # Fallback if drf-spectacular is not installed
    def extend_schema(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def OpenApiParameter(*args, **kwargs):
        return None
    
    def OpenApiExample(*args, **kwargs):
        return None

from django_bulk_drf.bulk_processing import (
    bulk_create_task,
    bulk_delete_task,
    bulk_get_task,
    bulk_replace_task,
    bulk_update_task,
)


class BulkOperationsMixin:
    """Mixin providing bulk operations through a single endpoint with different HTTP methods."""

    @action(detail=False, methods=["get"], url_path="bulk")
    def bulk_get(self, request):
        """
        Retrieve multiple instances by IDs or query parameters.
        
        Supports ID-based retrieval via ?ids=1,2,3 or complex filters in request body.
        Returns serialized data directly for small results, or task ID for large results.
        """
        return self._bulk_get(request)

    @extend_schema(
        operation_id="bulk_create",
        summary="Bulk Create Multiple Instances",
        description="Create multiple instances asynchronously. Supports JSON arrays and CSV file uploads.",
        request={
            'application/json': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'Instance ID (auto-generated for create)'},
                        # Additional properties will be dynamically added based on the serializer
                    },
                    'additionalProperties': True
                },
                'example': [
                    {"field1": "value1", "field2": "value2"},
                    {"field1": "value3", "field2": "value4"}
                ]
            }
        },
        responses={
            202: {
                'description': 'Task created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Bulk create task started for 2 items',
                            'task_id': 'abc123-def456-ghi789',
                            'total_items': 2,
                            'status_url': '/api/bulk-operations/abc123-def456-ghi789/status/'
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_create(self, request):
        """
        Create multiple instances asynchronously.
        
        Supports:
        - JSON: Content-Type: application/json - Array of objects to create
        - CSV: Content-Type: multipart/form-data - CSV file upload with headers
        
        Returns a task ID for tracking the bulk operation.
        """
        return self._handle_bulk_request(request, "create")

    @extend_schema(
        operation_id="bulk_update",
        summary="Bulk Update Multiple Instances",
        description="Update multiple instances asynchronously (partial updates).",
        request={
            'application/json': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'Instance ID to update', 'required': True},
                        # Additional properties will be dynamically added based on the serializer
                    },
                    'required': ['id'],
                    'additionalProperties': True
                },
                'example': [
                    {"id": 1, "field1": "updated_value1"},
                    {"id": 2, "field2": "updated_value2"}
                ]
            }
        },
        responses={
            202: {
                'description': 'Task created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Bulk update task started for 2 items',
                            'task_id': 'abc123-def456-ghi789',
                            'total_items': 2,
                            'status_url': '/api/bulk-operations/abc123-def456-ghi789/status/'
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=["patch"], url_path="bulk")
    def bulk_update(self, request):
        """
        Update multiple instances asynchronously (partial updates).
        
        Supports:
        - JSON: Content-Type: application/json - Array of objects with 'id' and fields to update
        - CSV: Content-Type: multipart/form-data - CSV file with 'id' column and fields to update
        
        Returns a task ID for tracking the bulk operation.
        """
        return self._handle_bulk_request(request, "update")

    @extend_schema(
        operation_id="bulk_replace",
        summary="Bulk Replace Multiple Instances",
        description="Replace multiple instances asynchronously (full updates).",
        request={
            'application/json': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'Instance ID to replace', 'required': True},
                        # Additional properties will be dynamically added based on the serializer
                    },
                    'required': ['id'],
                    'additionalProperties': True
                },
                'example': [
                    {"id": 1, "field1": "new_value1", "field2": "new_value2"},
                    {"id": 2, "field1": "new_value3", "field2": "new_value4"}
                ]
            }
        },
        responses={
            202: {
                'description': 'Task created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Bulk replace task started for 2 items',
                            'task_id': 'abc123-def456-ghi789',
                            'total_items': 2,
                            'status_url': '/api/bulk-operations/abc123-def456-ghi789/status/'
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=["put"], url_path="bulk")
    def bulk_replace(self, request):
        """
        Replace multiple instances asynchronously (full updates).
        
        Supports:
        - JSON: Content-Type: application/json - Array of complete objects with 'id' and all required fields
        - CSV: Content-Type: multipart/form-data - CSV file with 'id' column and all required fields
        
        Returns a task ID for tracking the bulk operation.
        """
        return self._handle_bulk_request(request, "replace")

    @extend_schema(
        operation_id="bulk_delete",
        summary="Bulk Delete Multiple Instances",
        description="Delete multiple instances asynchronously.",
        request={
            'application/json': {
                'type': 'array',
                'items': {'type': 'integer'},
                'example': [1, 2, 3, 4, 5]
            }
        },
        responses={
            202: {
                'description': 'Task created successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Bulk delete task started for 5 items',
                            'task_id': 'abc123-def456-ghi789',
                            'total_items': 5,
                            'status_url': '/api/bulk-operations/abc123-def456-ghi789/status/'
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=["delete"], url_path="bulk")
    def bulk_delete(self, request):
        """
        Delete multiple instances asynchronously.
        
        Supports:
        - JSON: Content-Type: application/json - Array of IDs to delete
        - CSV: Content-Type: multipart/form-data - CSV file with 'id' column
        
        Returns a task ID for tracking the bulk operation.
        """
        return self._handle_bulk_request(request, "delete")
    
    def _handle_bulk_request(self, request, operation: str):
        """
        Route bulk requests based on Content-Type header.
        
        Args:
            request: The HTTP request
            operation: The operation type (create, update, replace, delete)
        
        Returns:
            Response based on content type (JSON or CSV file upload)
        """
        content_type = request.content_type.lower() if request.content_type else ""
        
        # Check if this is a file upload (multipart/form-data)
        if content_type.startswith('multipart/form-data'):
            return self._bulk_csv(request, operation)
        
        # Default to JSON processing for application/json or other content types
        elif content_type.startswith('application/json') or request.data:
            if operation == "create":
                return self._bulk_create(request)
            elif operation == "update":
                return self._bulk_update(request)
            elif operation == "replace":
                return self._bulk_replace(request)
            elif operation == "delete":
                return self._bulk_delete(request)
        
        else:
            return Response(
                {
                    "error": "Unsupported content type. Use 'application/json' for JSON data or 'multipart/form-data' for CSV file upload.",
                    "supported_formats": {
                        "JSON": "Content-Type: application/json",
                        "CSV": "Content-Type: multipart/form-data with 'file' parameter"
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def _bulk_create(self, request):
        """
        Create multiple instances asynchronously.

        Expects a JSON array of objects to create.
        Returns a task ID for tracking the bulk operation.
        """
        data_list = request.data
        if not isinstance(data_list, list):
            return Response(
                {"error": "Expected a list of objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not data_list:
            return Response(
                {"error": "Empty list provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk create task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_create_task.delay(serializer_class_path, data_list, user_id)

        return Response(
            {
                "message": f"Bulk create task started for {len(data_list)} items",
                "task_id": task.id,
                "total_items": len(data_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _bulk_update(self, request):
        """
        Update multiple instances asynchronously.

        Expects a JSON array of objects with 'id' and update data.
        Returns a task ID for tracking the bulk operation.
        """
        updates_list = request.data
        if not isinstance(updates_list, list):
            return Response(
                {"error": "Expected a list of objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not updates_list:
            return Response(
                {"error": "Empty list provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that all items have an 'id' field
        for i, item in enumerate(updates_list):
            if not isinstance(item, dict) or "id" not in item:
                return Response(
                    {"error": f"Item at index {i} is missing 'id' field"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk update task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_update_task.delay(serializer_class_path, updates_list, user_id)

        return Response(
            {
                "message": f"Bulk update task started for {len(updates_list)} items",
                "task_id": task.id,
                "total_items": len(updates_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _bulk_replace(self, request):
        """
        Replace multiple instances asynchronously.

        Expects a JSON array of complete objects with 'id' and all required fields.
        Returns a task ID for tracking the bulk operation.
        """
        replacements_list = request.data
        if not isinstance(replacements_list, list):
            return Response(
                {"error": "Expected a list of objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not replacements_list:
            return Response(
                {"error": "Empty list provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that all items have an 'id' field
        for i, item in enumerate(replacements_list):
            if not isinstance(item, dict) or "id" not in item:
                return Response(
                    {"error": f"Item at index {i} is missing 'id' field"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk replace task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_replace_task.delay(serializer_class_path, replacements_list, user_id)

        return Response(
            {
                "message": f"Bulk replace task started for {len(replacements_list)} items",
                "task_id": task.id,
                "total_items": len(replacements_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _bulk_delete(self, request):
        """
        Delete multiple instances asynchronously.

        Expects a JSON array of IDs to delete.
        Returns a task ID for tracking the bulk operation.
        """
        ids_list = request.data
        if not isinstance(ids_list, list):
            return Response(
                {"error": "Expected a list of IDs"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not ids_list:
            return Response(
                {"error": "Empty list provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that all items are integers
        for i, item_id in enumerate(ids_list):
            if not isinstance(item_id, int):
                return Response(
                    {"error": f"Item at index {i} is not a valid integer ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk delete task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_delete_task.delay(serializer_class_path, ids_list, user_id)

        return Response(
            {
                "message": f"Bulk delete task started for {len(ids_list)} items",
                "task_id": task.id,
                "total_items": len(ids_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _bulk_get(self, request):
        """
        Retrieve multiple instances by IDs or query parameters.

        Supports:
        - Query params: ?ids=1,2,3 for simple ID-based retrieval
        - Request body: Complex filters for advanced queries

        Returns serialized data directly for small results, or task ID for large results.
        """
        # Check for simple ID-based retrieval via query params
        ids_param = request.query_params.get("ids")
        if ids_param:
            try:
                ids_list = [int(id_str.strip()) for id_str in ids_param.split(",") if id_str.strip()]
                if not ids_list:
                    return Response(
                        {"error": "No valid IDs provided"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                # For small result sets, return directly
                if len(ids_list) <= 100:  # Configurable threshold
                    return self._get_direct_results(ids_list)
                else:
                    # For large result sets, use async task
                    return self._get_async_results(ids_list)
                    
            except ValueError:
                return Response(
                    {"error": "Invalid ID format in query parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Check for complex query in request body
        elif request.data:
            query_filters = request.data
            if not isinstance(query_filters, dict):
                return Response(
                    {"error": "Expected a dictionary of filters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # For complex queries, always use async task
            return self._get_async_results_with_filters(query_filters)
        
        else:
            return Response(
                {
                    "error": "Must provide either 'ids' query parameter or request body with filters",
                    "examples": {
                        "simple": "GET /api/endpoint/bulk/?ids=1,2,3",
                        "complex": "GET /api/endpoint/bulk/ with JSON body containing filters"
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _get_direct_results(self, ids_list):
        """Get results directly for small result sets."""
        try:
            # Get the model class from the viewset
            model_class = self.get_queryset().model
            instances = model_class.objects.filter(id__in=ids_list)
            
            # Serialize the results
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(instances, many=True)
            
            return Response({
                "count": len(serializer.data),
                "results": serializer.data,
                "is_async": False
            })
            
        except Exception as e:
            return Response(
                {"error": f"Error retrieving results: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_async_results(self, ids_list):
        """Get results asynchronously for large result sets."""
        try:
            # Get the serializer class path
            serializer_class = self.get_serializer_class()
            serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"
            
            # Start the bulk get task
            user_id = self.request.user.id if self.request.user.is_authenticated else None
            task = bulk_get_task.delay(serializer_class_path, ids_list, user_id)
            
            return Response({
                "message": f"Bulk get task started for {len(ids_list)} items",
                "task_id": task.id,
                "total_items": len(ids_list),
                "status_url": f"/api/bulk-operations/{task.id}/status/",
                "is_async": True
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response(
                {"error": f"Error starting bulk get task: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_async_results_with_filters(self, query_filters):
        """Get results asynchronously using complex filters."""
        try:
            # Get the serializer class path
            serializer_class = self.get_serializer_class()
            serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"
            
            # Start the bulk get task with filters
            user_id = self.request.user.id if self.request.user.is_authenticated else None
            task = bulk_get_task.delay(serializer_class_path, query_filters, user_id, use_filters=True)
            
            return Response({
                "message": "Bulk get task started with complex filters",
                "task_id": task.id,
                "filters": query_filters,
                "status_url": f"/api/bulk-operations/{task.id}/status/",
                "is_async": True
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response(
                {"error": f"Error starting bulk get task: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _bulk_csv(self, request, operation: str):
        """
        Handle CSV file uploads for bulk operations.

        Args:
            request: The HTTP request
            operation: The operation type (create, update, replace, delete)

        Returns:
            Response with task ID for tracking
        """
        if "file" not in request.FILES:
            return Response(
                {
                    "error": "No file provided",
                    "supported_formats": ["CSV files with headers"]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        csv_file = request.FILES["file"]
        filename = csv_file.name

        # Validate file type
        if not filename.lower().endswith(".csv"):
            return Response(
                {"error": "File must be a CSV file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Read and parse CSV file
            import csv
            import io

            # Decode the file content
            content = csv_file.read().decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(content))
            data_list = list(csv_reader)

            if not data_list:
                return Response(
                    {"error": "CSV file is empty or has no data rows"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Process based on operation type
            if operation == "create":
                return self._process_csv_create(request, data_list, filename)
            elif operation == "update":
                return self._process_csv_update(request, data_list, filename)
            elif operation == "replace":
                return self._process_csv_replace(request, data_list, filename)
            elif operation == "delete":
                return self._process_csv_delete(request, data_list, filename)

        except UnicodeDecodeError:
            return Response(
                {"error": "CSV file must be UTF-8 encoded"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except csv.Error as e:
            return Response(
                {"error": f"Invalid CSV format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Error processing CSV file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _process_csv_create(self, request, data_list, filename):
        """Process CSV data for bulk create operation."""
        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk create task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_create_task.delay(serializer_class_path, data_list, user_id, source_file=filename)

        return Response(
            {
                "message": f"Bulk create task started from CSV file '{filename}' for {len(data_list)} items",
                "task_id": task.id,
                "total_items": len(data_list),
                "source_file": filename,
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _process_csv_update(self, request, data_list, filename):
        """Process CSV data for bulk update operation."""
        # Validate that all items have an 'id' column
        for i, item in enumerate(data_list):
            if "id" not in item:
                return Response(
                    {"error": f"Row {i+1} is missing 'id' column"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk update task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_update_task.delay(serializer_class_path, data_list, user_id, source_file=filename)

        return Response(
            {
                "message": f"Bulk update task started from CSV file '{filename}' for {len(data_list)} items",
                "task_id": task.id,
                "total_items": len(data_list),
                "source_file": filename,
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _process_csv_replace(self, request, data_list, filename):
        """Process CSV data for bulk replace operation."""
        # Validate that all items have an 'id' column
        for i, item in enumerate(data_list):
            if "id" not in item:
                return Response(
                    {"error": f"Row {i+1} is missing 'id' column"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk replace task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_replace_task.delay(serializer_class_path, data_list, user_id, source_file=filename)

        return Response(
            {
                "message": f"Bulk replace task started from CSV file '{filename}' for {len(data_list)} items",
                "task_id": task.id,
                "total_items": len(data_list),
                "source_file": filename,
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _process_csv_delete(self, request, data_list, filename):
        """Process CSV data for bulk delete operation."""
        # Extract IDs from the CSV data
        ids_list = []
        for i, item in enumerate(data_list):
            if "id" not in item:
                return Response(
                    {"error": f"Row {i+1} is missing 'id' column"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                ids_list.append(int(item["id"]))
            except (ValueError, TypeError):
                return Response(
                    {"error": f"Row {i+1} has invalid ID format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get the serializer class path
        serializer_class = self.get_serializer_class()
        serializer_class_path = f"{serializer_class.__module__}.{serializer_class.__name__}"

        # Start the bulk delete task
        user_id = request.user.id if request.user.is_authenticated else None
        task = bulk_delete_task.delay(serializer_class_path, ids_list, user_id, source_file=filename)

        return Response(
            {
                "message": f"Bulk delete task started from CSV file '{filename}' for {len(ids_list)} items",
                "task_id": task.id,
                "total_items": len(ids_list),
                "source_file": filename,
                "status_url": f"/api/bulk-operations/{task.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class BulkCreateMixin:
    """Mixin providing bulk create operations through a dedicated endpoint."""

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create_action(self, request):
        """
        Create multiple instances asynchronously through a dedicated endpoint.
        
        This is an alternative to the main bulk endpoint for create operations.
        """
        return self._bulk_create(request)


class BulkUpdateMixin:
    """Mixin providing bulk update operations through a dedicated endpoint."""

    @action(detail=False, methods=["patch"], url_path="bulk-update")
    def bulk_update_action(self, request):
        """
        Update multiple instances asynchronously through a dedicated endpoint.
        
        This is an alternative to the main bulk endpoint for update operations.
        """
        return self._bulk_update(request)


class BulkDeleteMixin:
    """Mixin providing bulk delete operations through a dedicated endpoint."""

    @action(detail=False, methods=["delete"], url_path="bulk-delete")
    def bulk_delete_action(self, request):
        """
        Delete multiple instances asynchronously through a dedicated endpoint.
        
        This is an alternative to the main bulk endpoint for delete operations.
        """
        return self._bulk_delete(request)


class BulkReplaceMixin:
    """Mixin providing bulk replace operations through a dedicated endpoint."""

    @action(detail=False, methods=["put"], url_path="bulk-replace")
    def bulk_replace_action(self, request):
        """
        Replace multiple instances asynchronously through a dedicated endpoint.
        
        This is an alternative to the main bulk endpoint for replace operations.
        """
        return self._bulk_replace(request)


class BulkGetMixin:
    """Mixin providing bulk get operations through a dedicated endpoint."""

    @action(detail=False, methods=["get"], url_path="bulk-get")
    def bulk_get_action(self, request):
        """
        Retrieve multiple instances through a dedicated endpoint.
        
        This is an alternative to the main bulk endpoint for get operations.
        """
        return self._bulk_get(request) 