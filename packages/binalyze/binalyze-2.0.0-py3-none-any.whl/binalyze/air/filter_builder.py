"""
Filter Builder for the Binalyze AIR SDK.

Provides a fluent interface for building filters with automatic validation
and type hints for better developer experience.
"""

from typing import List, Optional, Dict, Any, Union, Type, TypeVar
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
from .models.auto_asset_tags import AutoAssetTagFilter
from .models.event_subscription import EventSubscriptionFilter
from .models.user_management import UserFilter
from .models.notifications import NotificationsFilter
from .models.relay_server import RelayServersFilter


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
    
    # Add more filter builders as needed
    @staticmethod
    def asset_task() -> 'AssetTaskFilterBuilder':
        """Create a new asset task filter builder."""
        return AssetTaskFilterBuilder()
    
    @staticmethod
    def acquisition() -> 'AcquisitionFilterBuilder':
        """Create a new acquisition filter builder."""
        return AcquisitionFilterBuilder()


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


# Example usage patterns:
"""
# Asset filter examples:
asset_filter = assets().is_online().is_windows().add_organization(0).build()
asset_filter = assets().search_term("server").platform(["windows", "linux"]).build()
asset_filter = assets().last_seen_after("2024-01-01").tags(["critical", "production"]).build()

# Task filter examples:
task_filter = tasks().is_completed().is_acquisition().add_organization(0).build()
task_filter = tasks().status(["processing", "completed"]).task_type(["triage"]).build()

# Case filter examples:
case_filter = cases().is_open().is_high_priority().owner("admin").build()
case_filter = cases().created_after("2024-01-01").tags(["incident"]).build()

# Using the fluent interface as requested:
builder = filter_builder
my_filter = builder.asset().add_included_endpoints(['endpoint1']).add_organization(0).build()
""" 