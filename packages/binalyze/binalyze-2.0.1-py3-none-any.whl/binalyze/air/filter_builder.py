"""
Filter Builder for the Binalyze AIR SDK.

Provides a fluent interface for building filters with automatic validation
and type hints for better developer experience.
"""

from typing import List, Optional, Dict, Any, TypeVar, Union
from datetime import datetime
from abc import ABC, abstractmethod

# Type variable for preserving subclass types in method chaining
T = TypeVar('T', bound='FilterBuilderBase')

from .constants import (
    AssetStatus, AssetPlatform, AssetManagedStatus, AssetIsolationStatus,
    TaskStatus, TaskType, TaskExecutionType, CaseStatus, CasePriority,
    AcquisitionType, AcquisitionStatus, RepositoryType, AuditLevel,
    FilterOperator, FilterLogic, Defaults
)

# Import filter models
from .models.assets import AssetFilter, AssetTaskFilter
from .models.cases import CaseFilter, CaseActivityFilter, CaseEndpointFilter, CaseTaskFilter, CaseUserFilter
from .models.tasks import TaskFilter
from .models.acquisitions import AcquisitionFilter
from .models.organizations import OrganizationFilter
from .models.triage import TriageFilter
from .models.audit import AuditFilter, AuditLogsFilter
from .models.baseline import BaselineFilter
from .models.evidences import RepositoryFilter
from .models.auto_asset_tags import AutoAssetTagFilter, StartTaggingFilter
from .models.event_subscription import EventSubscriptionFilter
from .models.user_management import UserFilter, UserGroupFilter
from .models.notifications import NotificationsFilter
from .models.relay_server import RelayServersFilter
from .models.api_tokens import APITokenFilter
from .models.cloud_forensics import CloudAccountFilter
from .models.preset_filters import PresetFiltersFilter
from .models.policies import PolicyFilter
from .models.recent_activities import RecentActivitiesFilter
from .models.interact import LibraryFileFilter
from .models.backup import BackupFilter
from .models.investigation_hub import FindingsFilter


class FilterBuilderBase(ABC):
    """Base class for all filter builders."""
    
    def __init__(self):
        self._filter_data: Dict[str, Any] = {}
        self._organization_ids: List[int] = []
        self._included_endpoints: List[str] = []
        self._excluded_endpoints: List[str] = []
    
    @abstractmethod
    def build(self) -> Any:
        """Build and return the filter instance."""
        pass
    
    def add_organization(self: T, organization_id: int) -> T:
        """Add organization ID to filter."""
        if organization_id not in self._organization_ids:
            self._organization_ids.append(organization_id)
        return self
    
    def add_organizations(self: T, organization_ids: List[int]) -> T:
        """Add multiple organization IDs to filter."""
        for org_id in organization_ids:
            self.add_organization(org_id)
        return self
    
    def add_included_endpoint(self: T, endpoint_id: str) -> T:
        """Add endpoint ID to included endpoints."""
        if endpoint_id not in self._included_endpoints:
            self._included_endpoints.append(endpoint_id)
        return self
    
    def add_included_endpoints(self: T, endpoint_ids: List[str]) -> T:
        """Add multiple endpoint IDs to included endpoints."""
        for endpoint_id in endpoint_ids:
            self.add_included_endpoint(endpoint_id)
        return self
    
    def add_excluded_endpoint(self: T, endpoint_id: str) -> T:
        """Add endpoint ID to excluded endpoints."""
        if endpoint_id not in self._excluded_endpoints:
            self._excluded_endpoints.append(endpoint_id)
        return self
    
    def add_excluded_endpoints(self: T, endpoint_ids: List[str]) -> T:
        """Add multiple endpoint IDs to excluded endpoints."""
        for endpoint_id in endpoint_ids:
            self.add_excluded_endpoint(endpoint_id)
        return self
    
    def search_term(self: T, term: str) -> T:
        """Set search term for filter."""
        self._filter_data['search_term'] = term
        return self
    
    def _prepare_base_filter_data(self) -> Dict[str, Any]:
        """Prepare base filter data common to all filters."""
        data = self._filter_data.copy()
        
        if self._organization_ids:
            data['organization_ids'] = self._organization_ids
        
        if self._included_endpoints:
            data['included_endpoint_ids'] = self._included_endpoints
        
        if self._excluded_endpoints:
            data['excluded_endpoint_ids'] = self._excluded_endpoints
        
        return data


class AssetFilterBuilder(FilterBuilderBase):
    """Builder for asset filters with fluent interface."""
    
    def __init__(self):
        super().__init__()
    
    def name(self, name: str) -> 'AssetFilterBuilder':
        """Filter by asset name."""
        self._filter_data['name'] = name
        return self
    
    def ip_address(self, ip: str) -> 'AssetFilterBuilder':
        """Filter by IP address."""
        self._filter_data['ip_address'] = ip
        return self
    
    def group_id(self, group_id: str) -> 'AssetFilterBuilder':
        """Filter by group ID."""
        self._filter_data['group_id'] = group_id
        return self
    
    def group_path(self, path: str) -> 'AssetFilterBuilder':
        """Filter by group full path."""
        self._filter_data['group_full_path'] = path
        return self
    
    def managed_status(self, status: Union[str, List[str]]) -> 'AssetFilterBuilder':
        """Filter by managed status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['managed_status'] = status
        return self
    
    def online_status(self, status: Union[str, List[str]]) -> 'AssetFilterBuilder':
        """Filter by online status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['online_status'] = status
        return self
    
    def isolation_status(self, status: Union[str, List[str]]) -> 'AssetFilterBuilder':
        """Filter by isolation status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['isolation_status'] = status
        return self
    
    def platform(self, platform: Union[str, List[str]]) -> 'AssetFilterBuilder':
        """Filter by platform."""
        if isinstance(platform, str):
            platform = [platform]
        self._filter_data['platform'] = platform
        return self
    
    def issue(self, issue: Union[str, List[str]]) -> 'AssetFilterBuilder':
        """Filter by issue type."""
        if isinstance(issue, str):
            issue = [issue]
        self._filter_data['issue'] = issue
        return self
    
    def version(self, version: str) -> 'AssetFilterBuilder':
        """Filter by version."""
        self._filter_data['version'] = version
        return self
    
    def policy(self, policy: str) -> 'AssetFilterBuilder':
        """Filter by policy."""
        self._filter_data['policy'] = policy
        return self
    
    def tags(self, tags: Union[str, List[str]]) -> 'AssetFilterBuilder':
        """Filter by tags."""
        if isinstance(tags, str):
            tags = [tags]
        self._filter_data['tags'] = tags
        return self
    
    def tag_id(self, tag_id: str) -> 'AssetFilterBuilder':
        """Filter by tag ID."""
        self._filter_data['tag_id'] = tag_id
        return self
    
    def label(self, label: str) -> 'AssetFilterBuilder':
        """Filter by label."""
        self._filter_data['label'] = label
        return self
    
    def last_seen_before(self, date: Union[str, datetime]) -> 'AssetFilterBuilder':
        """Filter by last seen before date."""
        if isinstance(date, datetime):
            date = date.isoformat()
        self._filter_data['last_seen_before'] = date
        return self
    
    def last_seen_after(self, date: Union[str, datetime]) -> 'AssetFilterBuilder':
        """Filter by last seen after date."""
        if isinstance(date, datetime):
            date = date.isoformat()
        self._filter_data['last_seen_after'] = date
        return self
    
    def last_seen_between(self, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> 'AssetFilterBuilder':
        """Filter by last seen between dates."""
        if isinstance(start_date, datetime):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime):
            end_date = end_date.isoformat()
        self._filter_data['last_seen_between'] = f"{start_date},{end_date}"
        return self
    
    def aws_regions(self, regions: Union[str, List[str]]) -> 'AssetFilterBuilder':
        """Filter by AWS regions."""
        if isinstance(regions, str):
            regions = [regions]
        self._filter_data['aws_regions'] = regions
        return self
    
    def azure_regions(self, regions: Union[str, List[str]]) -> 'AssetFilterBuilder':
        """Filter by Azure regions."""
        if isinstance(regions, str):
            regions = [regions]
        self._filter_data['azure_regions'] = regions
        return self
    
    def is_managed(self) -> 'AssetFilterBuilder':
        """Filter for managed assets only."""
        return self.managed_status([AssetManagedStatus.MANAGED])
    
    def is_unmanaged(self) -> 'AssetFilterBuilder':
        """Filter for unmanaged assets only."""
        return self.managed_status([AssetManagedStatus.UNMANAGED])
    
    def is_online(self) -> 'AssetFilterBuilder':
        """Filter for online assets only."""
        return self.online_status([AssetStatus.ONLINE])
    
    def is_offline(self) -> 'AssetFilterBuilder':
        """Filter for offline assets only."""
        return self.online_status([AssetStatus.OFFLINE])
    
    def is_isolated(self) -> 'AssetFilterBuilder':
        """Filter for isolated assets only."""
        return self.isolation_status([AssetIsolationStatus.ISOLATED])
    
    def is_windows(self) -> 'AssetFilterBuilder':
        """Filter for Windows assets only."""
        return self.platform([AssetPlatform.WINDOWS])
    
    def is_linux(self) -> 'AssetFilterBuilder':
        """Filter for Linux assets only."""
        return self.platform([AssetPlatform.LINUX])
    
    def is_darwin(self) -> 'AssetFilterBuilder':
        """Filter for Darwin/macOS assets only."""
        return self.platform([AssetPlatform.DARWIN])
    
    def build(self) -> AssetFilter:
        """Build and return the AssetFilter instance."""
        data = self._prepare_base_filter_data()
        return AssetFilter(**data)


class TaskFilterBuilder(FilterBuilderBase):
    """Builder for task filters with fluent interface."""
    
    def __init__(self):
        super().__init__()
    
    def name(self, name: str) -> 'TaskFilterBuilder':
        """Filter by task name."""
        self._filter_data['name'] = name
        return self
    
    def status(self, status: Union[str, List[str]]) -> 'TaskFilterBuilder':
        """Filter by task status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['status'] = status
        return self
    
    def task_type(self, task_type: Union[str, List[str]]) -> 'TaskFilterBuilder':
        """Filter by task type."""
        if isinstance(task_type, str):
            task_type = [task_type]
        self._filter_data['type'] = task_type
        return self
    
    def execution_type(self, execution_type: Union[str, List[str]]) -> 'TaskFilterBuilder':
        """Filter by execution type."""
        if isinstance(execution_type, str):
            execution_type = [execution_type]
        self._filter_data['execution_type'] = execution_type
        return self
    
    def endpoint_ids(self, endpoint_ids: List[str]) -> 'TaskFilterBuilder':
        """Filter by endpoint IDs."""
        self._filter_data['endpoint_ids'] = endpoint_ids
        return self
    
    def is_completed(self) -> 'TaskFilterBuilder':
        """Filter for completed tasks only."""
        return self.status([TaskStatus.COMPLETED])
    
    def is_failed(self) -> 'TaskFilterBuilder':
        """Filter for failed tasks only."""
        return self.status([TaskStatus.FAILED])
    
    def is_processing(self) -> 'TaskFilterBuilder':
        """Filter for processing tasks only."""
        return self.status([TaskStatus.PROCESSING])
    
    def is_acquisition(self) -> 'TaskFilterBuilder':
        """Filter for acquisition tasks only."""
        return self.task_type([TaskType.ACQUISITION])
    
    def is_triage(self) -> 'TaskFilterBuilder':
        """Filter for triage tasks only."""
        return self.task_type([TaskType.TRIAGE])
    
    def is_instant(self) -> 'TaskFilterBuilder':
        """Filter for instant execution tasks only."""
        return self.execution_type([TaskExecutionType.INSTANT])
    
    def is_scheduled(self) -> 'TaskFilterBuilder':
        """Filter for scheduled execution tasks only."""
        return self.execution_type([TaskExecutionType.SCHEDULED])
    
    def build(self) -> TaskFilter:
        """Build and return the TaskFilter instance."""
        data = self._prepare_base_filter_data()
        return TaskFilter(**data)


class CaseFilterBuilder(FilterBuilderBase):
    """Builder for case filters with fluent interface."""
    
    def __init__(self):
        super().__init__()
    
    def name(self, name: str) -> 'CaseFilterBuilder':
        """Filter by case name."""
        self._filter_data['name'] = name
        return self
    
    def status(self, status: Union[str, List[str]]) -> 'CaseFilterBuilder':
        """Filter by case status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['status'] = status
        return self
    
    def priority(self, priority: Union[str, List[str]]) -> 'CaseFilterBuilder':
        """Filter by case priority."""
        if isinstance(priority, str):
            priority = [priority]
        self._filter_data['priority'] = priority
        return self
    
    def owner(self, owner: str) -> 'CaseFilterBuilder':
        """Filter by case owner."""
        self._filter_data['owner'] = owner
        return self
    
    def assignee(self, assignee: str) -> 'CaseFilterBuilder':
        """Filter by case assignee."""
        self._filter_data['assignee'] = assignee
        return self
    
    def tags(self, tags: Union[str, List[str]]) -> 'CaseFilterBuilder':
        """Filter by case tags."""
        if isinstance(tags, str):
            tags = [tags]
        self._filter_data['tags'] = tags
        return self
    
    def created_before(self, date: Union[str, datetime]) -> 'CaseFilterBuilder':
        """Filter by created before date."""
        if isinstance(date, datetime):
            date = date.isoformat()
        self._filter_data['created_before'] = date
        return self
    
    def created_after(self, date: Union[str, datetime]) -> 'CaseFilterBuilder':
        """Filter by created after date."""
        if isinstance(date, datetime):
            date = date.isoformat()
        self._filter_data['created_after'] = date
        return self
    
    def is_open(self) -> 'CaseFilterBuilder':
        """Filter for open cases only."""
        return self.status([CaseStatus.OPEN])
    
    def is_closed(self) -> 'CaseFilterBuilder':
        """Filter for closed cases only."""
        return self.status([CaseStatus.CLOSED])
    
    def is_archived(self) -> 'CaseFilterBuilder':
        """Filter for archived cases only."""
        return self.status([CaseStatus.ARCHIVED])
    
    def is_high_priority(self) -> 'CaseFilterBuilder':
        """Filter for high priority cases only."""
        return self.priority([CasePriority.HIGH])
    
    def is_critical_priority(self) -> 'CaseFilterBuilder':
        """Filter for critical priority cases only."""
        return self.priority([CasePriority.CRITICAL])
    
    def build(self) -> CaseFilter:
        """Build and return the CaseFilter instance."""
        data = self._prepare_base_filter_data()
        return CaseFilter(**data)


class AssetTaskFilterBuilder(FilterBuilderBase):
    """Builder for asset task filters."""
    
    def __init__(self):
        super().__init__()
    
    def name(self, name: str) -> 'AssetTaskFilterBuilder':
        """Filter by task name."""
        self._filter_data['name'] = name
        return self
    
    def status(self, status: Union[str, List[str]]) -> 'AssetTaskFilterBuilder':
        """Filter by task status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['status'] = status
        return self
    
    def task_type(self, task_type: Union[str, List[str]]) -> 'AssetTaskFilterBuilder':
        """Filter by task type."""
        if isinstance(task_type, str):
            task_type = [task_type]
        self._filter_data['type'] = task_type
        return self
    
    def execution_type(self, execution_type: Union[str, List[str]]) -> 'AssetTaskFilterBuilder':
        """Filter by execution type."""
        if isinstance(execution_type, str):
            execution_type = [execution_type]
        self._filter_data['execution_type'] = execution_type
        return self
    
    def has_drone_data(self, has_data: bool) -> 'AssetTaskFilterBuilder':
        """Filter by drone data presence."""
        self._filter_data['has_drone_data'] = "yes" if has_data else "no"
        return self
    
    def build(self) -> AssetTaskFilter:
        """Build and return the AssetTaskFilter instance."""
        data = self._prepare_base_filter_data()
        return AssetTaskFilter(**data)


class AcquisitionFilterBuilder(FilterBuilderBase):
    """Builder for acquisition filters."""
    
    def __init__(self):
        super().__init__()
    
    def profile_name(self, name: str) -> 'AcquisitionFilterBuilder':
        """Filter by acquisition profile name."""
        self._filter_data['profile_name'] = name
        return self
    
    def acquisition_type(self, acq_type: str) -> 'AcquisitionFilterBuilder':
        """Filter by acquisition type."""
        self._filter_data['type'] = acq_type
        return self
    
    def build(self) -> AcquisitionFilter:
        """Build and return the AcquisitionFilter instance."""
        data = self._prepare_base_filter_data()
        return AcquisitionFilter(**data)


class APITokenFilterBuilder(FilterBuilderBase):
    """Builder for API token filters."""
    
    def __init__(self):
        super().__init__()
    
    def page_size(self, size: int) -> 'APITokenFilterBuilder':
        """Set page size."""
        self._filter_data['pageSize'] = size
        return self
    
    def page_number(self, number: int) -> 'APITokenFilterBuilder':
        """Set page number."""
        self._filter_data['pageNumber'] = number
        return self
    
    def sort_by(self, field: str) -> 'APITokenFilterBuilder':
        """Set sort field (name, description, expirationDate, createdAt)."""
        self._filter_data['sortBy'] = field
        return self
    
    def sort_type(self, sort_type: str) -> 'APITokenFilterBuilder':
        """Set sort type (ASC or DESC)."""
        self._filter_data['sortType'] = sort_type
        return self
    
    def build(self) -> APITokenFilter:
        """Build and return the APITokenFilter instance."""
        data = self._prepare_base_filter_data()
        return APITokenFilter(**data)


class UserFilterBuilder(FilterBuilderBase):
    """Builder for user filters."""
    
    def __init__(self):
        super().__init__()
    
    def username(self, username: str) -> 'UserFilterBuilder':
        """Filter by username."""
        self._filter_data['username'] = username
        return self
    
    def email(self, email: str) -> 'UserFilterBuilder':
        """Filter by email."""
        self._filter_data['email'] = email
        return self
    
    def role(self, role: str) -> 'UserFilterBuilder':
        """Filter by role."""
        self._filter_data['role'] = role
        return self
    
    def organization_id(self, org_id: int) -> 'UserFilterBuilder':
        """Filter by organization ID."""
        self._filter_data['organizationId'] = org_id
        return self
    
    def is_active(self, active: bool = True) -> 'UserFilterBuilder':
        """Filter by active status."""
        self._filter_data['isActive'] = active
        return self
    
    def is_inactive(self) -> 'UserFilterBuilder':
        """Filter for inactive users only."""
        return self.is_active(False)
    
    def build(self) -> UserFilter:
        """Build and return the UserFilter instance."""
        data = self._prepare_base_filter_data()
        return UserFilter(**data)


class UserGroupFilterBuilder(FilterBuilderBase):
    """Builder for user group filters."""
    
    def __init__(self):
        super().__init__()
    
    def name(self, name: str) -> 'UserGroupFilterBuilder':
        """Filter by group name."""
        self._filter_data['name'] = name
        return self
    
    def description(self, description: str) -> 'UserGroupFilterBuilder':
        """Filter by group description."""
        self._filter_data['description'] = description
        return self
    
    def build(self) -> UserGroupFilter:
        """Build and return the UserGroupFilter instance."""
        data = self._prepare_base_filter_data()
        return UserGroupFilter(**data)


class AuditLogsFilterBuilder(FilterBuilderBase):
    """Builder for audit logs filters."""
    
    def __init__(self):
        super().__init__()
    
    def audit_type(self, audit_type: str) -> 'AuditLogsFilterBuilder':
        """Filter by audit log type."""
        self._filter_data['type'] = audit_type
        return self
    
    def performed_by(self, user: str) -> 'AuditLogsFilterBuilder':
        """Filter by user who performed the action."""
        self._filter_data['performed_by'] = user
        return self
    
    def endpoint_name(self, name: str) -> 'AuditLogsFilterBuilder':
        """Filter by endpoint name."""
        self._filter_data['endpoint_name'] = name
        return self
    
    def event_source(self, source: str) -> 'AuditLogsFilterBuilder':
        """Filter by event source."""
        self._filter_data['event_source'] = source
        return self
    
    def occurred_at(self, timestamp: str) -> 'AuditLogsFilterBuilder':
        """Filter by occurrence timestamp."""
        self._filter_data['occurred_at'] = timestamp
        return self
    
    def data_filter(self, data_filter: str) -> 'AuditLogsFilterBuilder':
        """Apply data filtering."""
        self._filter_data['data_filter'] = data_filter
        return self
    
    def all_organizations(self, all_orgs: bool = True) -> 'AuditLogsFilterBuilder':
        """Include all organizations."""
        self._filter_data['all_organizations'] = all_orgs
        return self
    
    def build(self) -> AuditLogsFilter:
        """Build and return the AuditLogsFilter instance."""
        data = self._prepare_base_filter_data()
        return AuditLogsFilter(**data)


class AuditFilterBuilder(FilterBuilderBase):
    """Builder for audit filters."""
    
    def __init__(self):
        super().__init__()
    
    def user_id(self, user_id: str) -> 'AuditFilterBuilder':
        """Filter by user ID."""
        self._filter_data['user_id'] = user_id
        return self
    
    def username(self, username: str) -> 'AuditFilterBuilder':
        """Filter by username."""
        self._filter_data['username'] = username
        return self
    
    def category(self, categories: Union[str, List[str]]) -> 'AuditFilterBuilder':
        """Filter by audit categories."""
        if isinstance(categories, str):
            categories = [categories]
        self._filter_data['category'] = categories
        return self
    
    def action(self, actions: Union[str, List[str]]) -> 'AuditFilterBuilder':
        """Filter by audit actions."""
        if isinstance(actions, str):
            actions = [actions]
        self._filter_data['action'] = actions
        return self
    
    def level(self, levels: Union[str, List[str]]) -> 'AuditFilterBuilder':
        """Filter by audit levels."""
        if isinstance(levels, str):
            levels = [levels]
        self._filter_data['level'] = levels
        return self
    
    def resource_type(self, resource_type: str) -> 'AuditFilterBuilder':
        """Filter by resource type."""
        self._filter_data['resource_type'] = resource_type
        return self
    
    def resource_id(self, resource_id: str) -> 'AuditFilterBuilder':
        """Filter by resource ID."""
        self._filter_data['resource_id'] = resource_id
        return self
    
    def ip_address(self, ip: str) -> 'AuditFilterBuilder':
        """Filter by IP address."""
        self._filter_data['ip_address'] = ip
        return self
    
    def success(self, success: bool = True) -> 'AuditFilterBuilder':
        """Filter by success status."""
        self._filter_data['success'] = success
        return self
    
    def failed(self) -> 'AuditFilterBuilder':
        """Filter for failed operations only."""
        return self.success(False)
    
    def start_date(self, date: Union[str, datetime]) -> 'AuditFilterBuilder':
        """Filter by start date."""
        if isinstance(date, datetime):
            date = date.isoformat()
        self._filter_data['start_date'] = date
        return self
    
    def end_date(self, date: Union[str, datetime]) -> 'AuditFilterBuilder':
        """Filter by end date."""
        if isinstance(date, datetime):
            date = date.isoformat()
        self._filter_data['end_date'] = date
        return self
    
    def tags(self, tags: Union[str, List[str]]) -> 'AuditFilterBuilder':
        """Filter by tags."""
        if isinstance(tags, str):
            tags = [tags]
        self._filter_data['tags'] = tags
        return self
    
    def correlation_id(self, correlation_id: str) -> 'AuditFilterBuilder':
        """Filter by correlation ID."""
        self._filter_data['correlation_id'] = correlation_id
        return self
    
    def build(self) -> AuditFilter:
        """Build and return the AuditFilter instance."""
        data = self._prepare_base_filter_data()
        return AuditFilter(**data)


class NotificationsFilterBuilder(FilterBuilderBase):
    """Builder for notifications filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> NotificationsFilter:
        """Build and return the NotificationsFilter instance."""
        data = self._prepare_base_filter_data()
        return NotificationsFilter(**data)


class OrganizationFilterBuilder(FilterBuilderBase):
    """Builder for organization filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> OrganizationFilter:
        """Build and return the OrganizationFilter instance."""
        data = self._prepare_base_filter_data()
        return OrganizationFilter(**data)


class TriageFilterBuilder(FilterBuilderBase):
    """Builder for triage filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> TriageFilter:
        """Build and return the TriageFilter instance."""
        data = self._prepare_base_filter_data()
        return TriageFilter(**data)


class RepositoryFilterBuilder(FilterBuilderBase):
    """Builder for repository (evidence) filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> RepositoryFilter:
        """Build and return the RepositoryFilter instance."""
        data = self._prepare_base_filter_data()
        return RepositoryFilter(**data)


class EventSubscriptionFilterBuilder(FilterBuilderBase):
    """Builder for event subscription filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> EventSubscriptionFilter:
        """Build and return the EventSubscriptionFilter instance."""
        data = self._prepare_base_filter_data()
        return EventSubscriptionFilter(**data)


class CaseActivityFilterBuilder(FilterBuilderBase):
    """Builder for case activity filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> CaseActivityFilter:
        """Build and return the CaseActivityFilter instance."""
        data = self._prepare_base_filter_data()
        return CaseActivityFilter(**data)


class CaseEndpointFilterBuilder(FilterBuilderBase):
    """Builder for case endpoint filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> CaseEndpointFilter:
        """Build and return the CaseEndpointFilter instance."""
        data = self._prepare_base_filter_data()
        return CaseEndpointFilter(**data)


class CaseTaskFilterBuilder(FilterBuilderBase):
    """Builder for case task filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> CaseTaskFilter:
        """Build and return the CaseTaskFilter instance."""
        data = self._prepare_base_filter_data()
        return CaseTaskFilter(**data)


class CaseUserFilterBuilder(FilterBuilderBase):
    """Builder for case user filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> CaseUserFilter:
        """Build and return the CaseUserFilter instance."""
        data = self._prepare_base_filter_data()
        return CaseUserFilter(**data)


class RelayServersFilterBuilder(FilterBuilderBase):
    """Builder for relay servers filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> RelayServersFilter:
        """Build and return the RelayServersFilter instance."""
        data = self._prepare_base_filter_data()
        return RelayServersFilter(**data)


class AutoAssetTagFilterBuilder(FilterBuilderBase):
    """Builder for auto asset tag filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> AutoAssetTagFilter:
        """Build and return the AutoAssetTagFilter instance."""
        data = self._prepare_base_filter_data()
        return AutoAssetTagFilter(**data)


class BaselineFilterBuilder(FilterBuilderBase):
    """Builder for baseline filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> BaselineFilter:
        """Build and return the BaselineFilter instance."""
        data = self._prepare_base_filter_data()
        return BaselineFilter(**data)


class CloudAccountFilterBuilder(FilterBuilderBase):
    """Builder for cloud account filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> CloudAccountFilter:
        """Build and return the CloudAccountFilter instance."""
        data = self._prepare_base_filter_data()
        return CloudAccountFilter(**data)


class PresetFiltersFilterBuilder(FilterBuilderBase):
    """Builder for preset filters filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> PresetFiltersFilter:
        """Build and return the PresetFiltersFilter instance."""
        data = self._prepare_base_filter_data()
        return PresetFiltersFilter(**data)


class PolicyFilterBuilder(FilterBuilderBase):
    """Builder for policy filters."""
    
    def __init__(self):
        super().__init__()
    
    def build(self) -> PolicyFilter:
        """Build and return the PolicyFilter instance."""
        data = self._prepare_base_filter_data()
        return PolicyFilter(**data)


class RecentActivitiesFilterBuilder(FilterBuilderBase):
    """Builder for recent activities filters."""
    
    def __init__(self):
        super().__init__()
    
    def activity_type(self, activity_type: str) -> 'RecentActivitiesFilterBuilder':
        """Filter by activity type."""
        self._filter_data['type'] = activity_type
        return self
    
    def username(self, username: str) -> 'RecentActivitiesFilterBuilder':
        """Filter by username."""
        self._filter_data['username'] = username
        return self
    
    def organization_id(self, org_id: int) -> 'RecentActivitiesFilterBuilder':
        """Filter by organization ID."""
        self._filter_data['organization_id'] = org_id
        return self
    
    def page_size(self, size: int) -> 'RecentActivitiesFilterBuilder':
        """Set page size."""
        self._filter_data['page_size'] = size
        return self
    
    def page_number(self, number: int) -> 'RecentActivitiesFilterBuilder':
        """Set page number."""
        self._filter_data['page_number'] = number
        return self
    
    def sort_by(self, field: str) -> 'RecentActivitiesFilterBuilder':
        """Set sort field."""
        self._filter_data['sort_by'] = field
        return self
    
    def sort_type(self, sort_type: str) -> 'RecentActivitiesFilterBuilder':
        """Set sort type (ASC or DESC)."""
        self._filter_data['sort_type'] = sort_type
        return self
    
    def build(self) -> RecentActivitiesFilter:
        """Build and return the RecentActivitiesFilter instance."""
        data = self._prepare_base_filter_data()
        return RecentActivitiesFilter(**data)


class LibraryFileFilterBuilder(FilterBuilderBase):
    """Builder for library file filters (interact module)."""
    
    def __init__(self):
        super().__init__()
    
    def name(self, name: str) -> 'LibraryFileFilterBuilder':
        """Filter by file name."""
        self._filter_data['name'] = name
        return self
    
    def uploaded_by(self, username: str) -> 'LibraryFileFilterBuilder':
        """Filter by uploader username."""
        self._filter_data['uploaded_by'] = username
        return self
    
    def uploaded_at(self, date: str) -> 'LibraryFileFilterBuilder':
        """Filter by upload date."""
        self._filter_data['uploaded_at'] = date
        return self
    
    def organization_ids(self, org_ids: List[int]) -> 'LibraryFileFilterBuilder':
        """Filter by organization IDs."""
        self._filter_data['organization_ids'] = org_ids
        return self
    
    def build(self) -> LibraryFileFilter:
        """Build and return the LibraryFileFilter instance."""
        data = self._prepare_base_filter_data()
        return LibraryFileFilter(**data)


class BackupFilterBuilder(FilterBuilderBase):
    """Builder for backup filters."""
    
    def __init__(self):
        super().__init__()
    
    def username(self, username: str) -> 'BackupFilterBuilder':
        """Filter by backup username."""
        self._filter_data['username'] = username
        return self
    
    def source(self, source: str) -> 'BackupFilterBuilder':
        """Filter by backup source (user, scheduler)."""
        self._filter_data['source'] = source
        return self
    
    def status(self, status: str) -> 'BackupFilterBuilder':
        """Filter by backup status."""
        self._filter_data['status'] = status
        return self
    
    def location(self, location: str) -> 'BackupFilterBuilder':
        """Filter by backup location (local, sftp, s3)."""
        self._filter_data['location'] = location
        return self
    
    def start_date(self, date: Union[str, datetime]) -> 'BackupFilterBuilder':
        """Filter by start date."""
        if isinstance(date, datetime):
            date = date.isoformat()
        self._filter_data['start_date'] = date
        return self
    
    def end_date(self, date: Union[str, datetime]) -> 'BackupFilterBuilder':
        """Filter by end date."""
        if isinstance(date, datetime):
            date = date.isoformat()
        self._filter_data['end_date'] = date
        return self
    
    def page_size(self, size: int) -> 'BackupFilterBuilder':
        """Set page size."""
        self._filter_data['pageSize'] = size
        return self
    
    def page_number(self, number: int) -> 'BackupFilterBuilder':
        """Set page number."""
        self._filter_data['pageNumber'] = number
        return self
    
    def sort_by(self, field: str) -> 'BackupFilterBuilder':
        """Set sort field."""
        self._filter_data['sortBy'] = field
        return self
    
    def sort_type(self, sort_type: str) -> 'BackupFilterBuilder':
        """Set sort type (ASC or DESC)."""
        self._filter_data['sortType'] = sort_type
        return self
    
    def build(self) -> BackupFilter:
        """Build and return the BackupFilter instance."""
        data = self._prepare_base_filter_data()
        return BackupFilter(**data)


class FindingsFilterBuilder(FilterBuilderBase):
    """Builder for investigation hub findings filters."""
    
    def __init__(self):
        super().__init__()
    
    def assignment_ids(self, assignment_ids: List[str]) -> 'FindingsFilterBuilder':
        """Filter by assignment IDs."""
        self._filter_data['assignment_ids'] = assignment_ids
        return self
    
    def flag_ids(self, flag_ids: List[int]) -> 'FindingsFilterBuilder':
        """Filter by flag IDs."""
        self._filter_data['flag_ids'] = flag_ids
        return self
    
    def verdict_scores(self, scores: List[str]) -> 'FindingsFilterBuilder':
        """Filter by verdict scores."""
        self._filter_data['verdict_scores'] = scores
        return self
    
    def created_by(self, users: List[str]) -> 'FindingsFilterBuilder':
        """Filter by created by users."""
        self._filter_data['created_by'] = users
        return self
    
    def mitre_technique_ids(self, technique_ids: List[str]) -> 'FindingsFilterBuilder':
        """Filter by MITRE technique IDs."""
        self._filter_data['mitre_technique_ids'] = technique_ids
        return self
    
    def mitre_tactic_ids(self, tactic_ids: List[str]) -> 'FindingsFilterBuilder':
        """Filter by MITRE tactic IDs."""
        self._filter_data['mitre_tactic_ids'] = tactic_ids
        return self
    
    def build(self) -> FindingsFilter:
        """Build and return the FindingsFilter instance."""
        data = self._prepare_base_filter_data()
        return FindingsFilter(**data)


class StartTaggingFilterBuilder(FilterBuilderBase):
    """Builder for start tagging filters (auto asset tagging)."""
    
    def __init__(self):
        super().__init__()
    
    def search_term(self, search_term: str) -> 'StartTaggingFilterBuilder':
        """Filter by search term."""
        self._filter_data['searchTerm'] = search_term
        return self
    
    def name(self, name: str) -> 'StartTaggingFilterBuilder':
        """Filter by asset name."""
        self._filter_data['name'] = name
        return self
    
    def ip_address(self, ip_address: str) -> 'StartTaggingFilterBuilder':
        """Filter by IP address."""
        self._filter_data['ipAddress'] = ip_address
        return self
    
    def group_id(self, group_id: str) -> 'StartTaggingFilterBuilder':
        """Filter by group ID."""
        self._filter_data['groupId'] = group_id
        return self
    
    def group_full_path(self, path: str) -> 'StartTaggingFilterBuilder':
        """Filter by group full path."""
        self._filter_data['groupFullPath'] = path
        return self
    
    def label(self, label: str) -> 'StartTaggingFilterBuilder':
        """Filter by label."""
        self._filter_data['label'] = label
        return self
    
    def last_seen(self, last_seen: str) -> 'StartTaggingFilterBuilder':
        """Filter by last seen."""
        self._filter_data['lastSeen'] = last_seen
        return self
    
    def managed_status(self, status: Union[str, List[str]]) -> 'StartTaggingFilterBuilder':
        """Filter by managed status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['managedStatus'] = status
        return self
    
    def isolation_status(self, status: Union[str, List[str]]) -> 'StartTaggingFilterBuilder':
        """Filter by isolation status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['isolationStatus'] = status
        return self
    
    def platform(self, platform: Union[str, List[str]]) -> 'StartTaggingFilterBuilder':
        """Filter by platform."""
        if isinstance(platform, str):
            platform = [platform]
        self._filter_data['platform'] = platform
        return self
    
    def issue(self, issue: str) -> 'StartTaggingFilterBuilder':
        """Filter by issue type."""
        self._filter_data['issue'] = issue
        return self
    
    def online_status(self, status: Union[str, List[str]]) -> 'StartTaggingFilterBuilder':
        """Filter by online status."""
        if isinstance(status, str):
            status = [status]
        self._filter_data['onlineStatus'] = status
        return self
    
    def tags(self, tags: Union[str, List[str]]) -> 'StartTaggingFilterBuilder':
        """Filter by tags."""
        if isinstance(tags, str):
            tags = [tags]
        self._filter_data['tags'] = tags
        return self
    
    def version(self, version: str) -> 'StartTaggingFilterBuilder':
        """Filter by version."""
        self._filter_data['version'] = version
        return self
    
    def policy(self, policy: str) -> 'StartTaggingFilterBuilder':
        """Filter by policy."""
        self._filter_data['policy'] = policy
        return self
    
    def included_endpoint_ids(self, endpoint_ids: List[str]) -> 'StartTaggingFilterBuilder':
        """Set included endpoint IDs."""
        self._filter_data['includedEndpointIds'] = endpoint_ids
        return self
    
    def excluded_endpoint_ids(self, endpoint_ids: List[str]) -> 'StartTaggingFilterBuilder':
        """Set excluded endpoint IDs."""
        self._filter_data['excludedEndpointIds'] = endpoint_ids
        return self
    
    def case_id(self, case_id: str) -> 'StartTaggingFilterBuilder':
        """Filter by case ID."""
        self._filter_data['caseId'] = case_id
        return self
    
    def organization_ids(self, org_ids: List[int]) -> 'StartTaggingFilterBuilder':
        """Set organization IDs (required)."""
        self._filter_data['organizationIds'] = org_ids
        return self
    
    # Convenience methods
    def is_managed(self) -> 'StartTaggingFilterBuilder':
        """Filter for managed assets only."""
        return self.managed_status([AssetManagedStatus.MANAGED])
    
    def is_unmanaged(self) -> 'StartTaggingFilterBuilder':
        """Filter for unmanaged assets only."""
        return self.managed_status([AssetManagedStatus.UNMANAGED])
    
    def is_online(self) -> 'StartTaggingFilterBuilder':
        """Filter for online assets only."""
        return self.online_status([AssetStatus.ONLINE])
    
    def is_offline(self) -> 'StartTaggingFilterBuilder':
        """Filter for offline assets only."""
        return self.online_status([AssetStatus.OFFLINE])
    
    def is_windows(self) -> 'StartTaggingFilterBuilder':
        """Filter for Windows assets only."""
        return self.platform([AssetPlatform.WINDOWS])
    
    def is_linux(self) -> 'StartTaggingFilterBuilder':
        """Filter for Linux assets only."""
        return self.platform([AssetPlatform.LINUX])
    
    def is_macos(self) -> 'StartTaggingFilterBuilder':
        """Filter for macOS assets only."""
        return self.platform([AssetPlatform.DARWIN])
    
    def build(self) -> StartTaggingFilter:
        """Build and return the StartTaggingFilter instance."""
        data = self._filter_data.copy()
        return StartTaggingFilter(**data)


class FilterBuilder:
    """Main filter builder factory class."""
    
    @staticmethod
    def asset() -> AssetFilterBuilder:
        """Create a new asset filter builder."""
        return AssetFilterBuilder()
    
    @staticmethod
    def task() -> TaskFilterBuilder:
        """Create a new task filter builder."""
        return TaskFilterBuilder()
        
    @staticmethod
    def case() -> CaseFilterBuilder:
        """Create a new case filter builder."""
        return CaseFilterBuilder()
    
    @staticmethod
    def asset_task() -> AssetTaskFilterBuilder:
        """Create a new asset task filter builder."""
        return AssetTaskFilterBuilder()
    
    @staticmethod
    def acquisition() -> AcquisitionFilterBuilder:
        """Create a new acquisition filter builder."""
        return AcquisitionFilterBuilder()
    
    @staticmethod
    def api_token() -> APITokenFilterBuilder:
        """Create a new API token filter builder."""
        return APITokenFilterBuilder()
        
    @staticmethod
    def user() -> UserFilterBuilder:
        """Create a new user filter builder."""
        return UserFilterBuilder()
        
    @staticmethod
    def user_group() -> UserGroupFilterBuilder:
        """Create a new user group filter builder."""
        return UserGroupFilterBuilder()
        
    @staticmethod
    def audit_logs() -> AuditLogsFilterBuilder:
        """Create a new audit logs filter builder."""
        return AuditLogsFilterBuilder()
        
    @staticmethod
    def audit() -> AuditFilterBuilder:
        """Create a new audit filter builder."""
        return AuditFilterBuilder()
        
    @staticmethod
    def notifications() -> NotificationsFilterBuilder:
        """Create a new notifications filter builder."""
        return NotificationsFilterBuilder()
        
    @staticmethod
    def organization() -> OrganizationFilterBuilder:
        """Create a new organization filter builder."""
        return OrganizationFilterBuilder()
        
    @staticmethod
    def triage() -> TriageFilterBuilder:
        """Create a new triage filter builder."""
        return TriageFilterBuilder()
        
    @staticmethod
    def repository() -> RepositoryFilterBuilder:
        """Create a new repository filter builder."""
        return RepositoryFilterBuilder()
        
    @staticmethod
    def event_subscription() -> EventSubscriptionFilterBuilder:
        """Create a new event subscription filter builder."""
        return EventSubscriptionFilterBuilder()
        
    @staticmethod
    def case_activity() -> CaseActivityFilterBuilder:
        """Create a new case activity filter builder."""
        return CaseActivityFilterBuilder()
        
    @staticmethod
    def case_endpoint() -> CaseEndpointFilterBuilder:
        """Create a new case endpoint filter builder."""
        return CaseEndpointFilterBuilder()
        
    @staticmethod
    def case_task() -> CaseTaskFilterBuilder:
        """Create a new case task filter builder."""
        return CaseTaskFilterBuilder()
        
    @staticmethod
    def case_user() -> CaseUserFilterBuilder:
        """Create a new case user filter builder."""
        return CaseUserFilterBuilder()
        
    @staticmethod
    def relay_servers() -> RelayServersFilterBuilder:
        """Create a new relay servers filter builder."""
        return RelayServersFilterBuilder()
        
    @staticmethod
    def auto_asset_tag() -> AutoAssetTagFilterBuilder:
        """Create a new auto asset tag filter builder."""
        return AutoAssetTagFilterBuilder()
        
    @staticmethod
    def baseline() -> BaselineFilterBuilder:
        """Create a new baseline filter builder."""
        return BaselineFilterBuilder()
        
    @staticmethod
    def cloud_account() -> CloudAccountFilterBuilder:
        """Create a new cloud account filter builder."""
        return CloudAccountFilterBuilder()
        
    @staticmethod
    def preset_filters() -> PresetFiltersFilterBuilder:
        """Create a preset filters filter builder."""
        return PresetFiltersFilterBuilder()
    
    @staticmethod
    def policies() -> PolicyFilterBuilder:
        """Create a policy filter builder."""
        return PolicyFilterBuilder()
    
    @staticmethod
    def recent_activities() -> RecentActivitiesFilterBuilder:
        """Create a recent activities filter builder."""
        return RecentActivitiesFilterBuilder()
    
    @staticmethod
    def library_files() -> LibraryFileFilterBuilder:
        """Create a library files filter builder."""
        return LibraryFileFilterBuilder()
    
    @staticmethod
    def backups() -> BackupFilterBuilder:
        """Create a backup filter builder."""
        return BackupFilterBuilder()
    
    @staticmethod
    def findings() -> FindingsFilterBuilder:
        """Create a new findings filter builder."""
        return FindingsFilterBuilder()
    
    @staticmethod
    def start_tagging() -> StartTaggingFilterBuilder:
        """Create a new start tagging filter builder."""
        return StartTaggingFilterBuilder()


# Global filter builder instance
filter_builder = FilterBuilder()

# Convenience functions for common patterns
def assets() -> AssetFilterBuilder:
    """Create a new asset filter builder."""
    return FilterBuilder.asset()

def tasks() -> TaskFilterBuilder:
    """Create a new task filter builder."""
    return FilterBuilder.task()

def cases() -> CaseFilterBuilder:
    """Create a new case filter builder."""
    return FilterBuilder.case()

def asset_tasks() -> AssetTaskFilterBuilder:
    """Create a new asset task filter builder."""
    return FilterBuilder.asset_task()

def acquisitions() -> AcquisitionFilterBuilder:
    """Create a new acquisition filter builder."""
    return FilterBuilder.acquisition()

def api_tokens() -> APITokenFilterBuilder:
    """Create a new API token filter builder."""
    return FilterBuilder.api_token()

def users() -> UserFilterBuilder:
    """Create a new user filter builder."""
    return FilterBuilder.user()

def user_groups() -> UserGroupFilterBuilder:
    """Create a new user group filter builder."""
    return FilterBuilder.user_group()

def audit_logs() -> AuditLogsFilterBuilder:
    """Create a new audit logs filter builder."""
    return FilterBuilder.audit_logs()

def audit() -> AuditFilterBuilder:
    """Create a new audit filter builder."""
    return FilterBuilder.audit()

def notifications() -> NotificationsFilterBuilder:
    """Create a new notifications filter builder."""
    return FilterBuilder.notifications()

def organizations() -> OrganizationFilterBuilder:
    """Create a new organization filter builder."""
    return FilterBuilder.organization()

def triage() -> TriageFilterBuilder:
    """Create a new triage filter builder."""
    return FilterBuilder.triage()

def repositories() -> RepositoryFilterBuilder:
    """Create a new repository filter builder."""
    return FilterBuilder.repository()

def event_subscriptions() -> EventSubscriptionFilterBuilder:
    """Create a new event subscription filter builder."""
    return FilterBuilder.event_subscription()

def case_activities() -> CaseActivityFilterBuilder:
    """Create a new case activity filter builder."""
    return FilterBuilder.case_activity()

def case_endpoints() -> CaseEndpointFilterBuilder:
    """Create a new case endpoint filter builder."""
    return FilterBuilder.case_endpoint()

def case_tasks() -> CaseTaskFilterBuilder:
    """Create a new case task filter builder."""
    return FilterBuilder.case_task()

def case_users() -> CaseUserFilterBuilder:
    """Create a new case user filter builder."""
    return FilterBuilder.case_user()

def relay_servers() -> RelayServersFilterBuilder:
    """Create a new relay servers filter builder."""
    return FilterBuilder.relay_servers()

def auto_asset_tags() -> AutoAssetTagFilterBuilder:
    """Create a new auto asset tag filter builder."""
    return FilterBuilder.auto_asset_tag()

def baselines() -> BaselineFilterBuilder:
    """Create a new baseline filter builder."""
    return FilterBuilder.baseline()

def cloud_accounts() -> CloudAccountFilterBuilder:
    """Create a new cloud account filter builder."""
    return FilterBuilder.cloud_account()

def preset_filters() -> PresetFiltersFilterBuilder:
    """Create a new preset filters filter builder."""
    return FilterBuilder.preset_filters()

def policies() -> PolicyFilterBuilder:
    """Create a new policy filter builder."""
    return FilterBuilder.policies()

def recent_activities() -> RecentActivitiesFilterBuilder:
    """Create a new recent activities filter builder."""
    return FilterBuilder.recent_activities()

def library_files() -> LibraryFileFilterBuilder:
    """Create a new library files filter builder."""
    return FilterBuilder.library_files()

def backups() -> BackupFilterBuilder:
    """Create a new backup filter builder."""
    return FilterBuilder.backups()

def findings() -> FindingsFilterBuilder:
    """Create a new findings filter builder."""
    return FilterBuilder.findings()

def start_tagging() -> StartTaggingFilterBuilder:
    """Create a new start tagging filter builder."""
    return FilterBuilder.start_tagging()


# Example usage patterns:
"""
# Asset filter examples:
asset_filter = assets().is_online().is_windows().add_organization(0).build()
asset_filter = assets().search_term("server").platform([AssetPlatform.WINDOWS, AssetPlatform.LINUX]).build()
asset_filter = assets().last_seen_after("2024-01-01").tags([CasePriority.CRITICAL, "production"]).build()

# Task filter examples:
task_filter = tasks().is_completed().is_acquisition().add_organization(0).build()
task_filter = tasks().status([TaskStatus.PROCESSING, TaskStatus.COMPLETED]).task_type([TaskType.TRIAGE]).build()

# Case filter examples:
case_filter = cases().is_open().is_high_priority().owner("admin").build()
case_filter = cases().created_after("2024-01-01").tags(["incident"]).build()

# Using the fluent interface as requested:
builder = filter_builder
my_filter = builder.asset().add_included_endpoints(['endpoint1']).add_organization(0).build()
""" 

__all__ = [
    # Base classes
    'FilterBuilderBase',
    'FilterBuilder',
    
    # Filter builders
    'AssetFilterBuilder',
    'TaskFilterBuilder',
    'CaseFilterBuilder',
    'AssetTaskFilterBuilder',
    'AcquisitionFilterBuilder',
    'APITokenFilterBuilder',
    'UserFilterBuilder',
    'UserGroupFilterBuilder',
    'AuditLogsFilterBuilder',
    'AuditFilterBuilder',
    'NotificationsFilterBuilder',
    'OrganizationFilterBuilder',
    'TriageFilterBuilder',
    'RepositoryFilterBuilder',
    'EventSubscriptionFilterBuilder',
    'CaseActivityFilterBuilder',
    'CaseEndpointFilterBuilder',
    'CaseTaskFilterBuilder',
    'CaseUserFilterBuilder',
    'RelayServersFilterBuilder',
    'AutoAssetTagFilterBuilder',
    'BaselineFilterBuilder',
    'CloudAccountFilterBuilder',
    'PresetFiltersFilterBuilder',
    'PolicyFilterBuilder',
    'RecentActivitiesFilterBuilder',
    'LibraryFileFilterBuilder',
    'BackupFilterBuilder',
    'FindingsFilterBuilder',
    'StartTaggingFilterBuilder',
    
    # Convenience functions
    'assets',
    'tasks', 
    'cases',
    'asset_tasks',
    'acquisitions',
    'api_tokens',
    'users',
    'user_groups',
    'audit_logs',
    'audit',
    'notifications',
    'organizations',
    'triage',
    'repositories',
    'event_subscriptions',
    'case_activities',
    'case_endpoints',
    'case_tasks',
    'case_users',
    'relay_servers',
    'auto_asset_tags',
    'baselines',
    'cloud_accounts',
    'preset_filters',
    'policies',
    'recent_activities',
    'library_files',
    'backups',
    'findings',
    'start_tagging',
] 