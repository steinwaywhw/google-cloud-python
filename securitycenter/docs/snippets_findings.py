#!/usr/bin/env python
#
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Examples of working with source and findings in Cloud Security Command Center."""
import os
import pytest


@pytest.fixture(scope="module")
def organization_id():
    """Get Organization ID from the environment variable """
    return os.environ["GCLOUD_ORGANIZATION"]


@pytest.fixture(scope="module")
def source_name(organization_id):
    from google.cloud import securitycenter as securitycenter

    client = securitycenter.SecurityCenterClient()
    org_name = "organizations/{org_id}".format(org_id=organization_id)

    source = client.create_source(
        org_name,
        {
            "display_name": "Unit test source",
            "description": "A new custom source that does X",
        },
    )
    return source.name


def test_create_source(organization_id):
    """ Create a new findings source. """
    # [START create_source]
    from google.cloud import securitycenter as securitycenter

    client = securitycenter.SecurityCenterClient()
    # organization_id is the numeric ID of the organization. e.g.:
    # organization_id = "111122222444"
    org_name = "organizations/{org_id}".format(org_id=organization_id)

    client.create_source(
        org_name,
        {
            "display_name": "Customized Display Name",
            "description": "A new custom source that does X",
        },
    )
    # [END create_source]


def test_list_source(organization_id):
    """ Create a new findings source. """
    i = -1
    # [START list_sources]
    from google.cloud import securitycenter as securitycenter

    # Create a new client.
    client = securitycenter.SecurityCenterClient()
    # organization_id is the numeric ID of the organization. e.g.:
    # organization_id = "111122222444"
    org_name = "organizations/{org_id}".format(org_id=organization_id)

    # Call the API and print out each existing source.
    for i, source in enumerate(client.list_sources(org_name)):
        print(i, source)
    # [END list_sources]
    assert i >= 0


def test_create_finding(source_name):
    """Demonstrate listing and printing all assets."""
    # [START create_finding]
    from google.cloud import securitycenter as securitycenter
    from google.cloud.securitycenter_v1.proto.finding_pb2 import Finding
    from google.protobuf.timestamp_pb2 import Timestamp

    # Create a new client.
    client = securitycenter.SecurityCenterClient()

    # Use the current time as the finding "event time".
    now_proto = Timestamp()
    now_proto.GetCurrentTime()

    # source_name is the resource path for a source that has been
    # created previously (you can use list_sources to find a specific one).
    # Its format is:
    # source_name = "organizations/{organization_id}/sources/{source_id}"
    # e.g.:
    # source_name = "organizations/111122222444/sources/1234"

    # Controlled by caller.
    finding_id = "samplefindingid"

    # The resource this finding applies to.  The CSCC UI can link
    # the findings for a resource to the corresponding Asset of a resource
    # if there are matches.
    resource_name = "//cloudresourcemanager.googleapis.com/organizations/11232"

    # Call The API.
    created_finding = client.create_finding(
        source_name,
        finding_id,
        {
            "state": Finding.ACTIVE,
            "resource_name": resource_name,
            "category": "MEDIUM_RISK_ONE",
            "event_time": now_proto,
        },
    )
    print(created_finding)
    # [END create_finding]
    assert len(created_finding.name) > 0


def test_create_finding_with_source_properties(source_name):
    """Demonstrate creating a new finding with source properties. """
    # [START create_finding_with_properties]
    from google.cloud import securitycenter as securitycenter
    from google.cloud.securitycenter_v1.proto.finding_pb2 import Finding
    from google.protobuf.timestamp_pb2 import Timestamp
    from google.protobuf.struct_pb2 import Value

    # Create a new client.
    client = securitycenter.SecurityCenterClient()

    # source_name is the resource path for a source that has been
    # created previously (you can use list_sources to find a specific one).
    # Its format is:
    # source_name = "organizations/{organization_id}/sources/{source_id}"
    # e.g.:
    # source_name = "organizations/111122222444/sources/1234"

    # Controlled by caller.
    finding_id = "samplefindingid2"

    # The resource this finding applies to.  The CSCC UI can link
    # the findings for a resource to the corresponding Asset of a resource
    # if there are matches.
    resource_name = "//cloudresourcemanager.googleapis.com/organizations/11232"

    # Define source properties values as protobuf "Value" objects.
    str_value = Value()
    str_value.string_value = "string_example"
    num_value = Value()
    num_value.number_value = 1234

    # Use the current time as the finding "event time".
    now_proto = Timestamp()
    now_proto.GetCurrentTime()

    created_finding = client.create_finding(
        source_name,
        finding_id,
        {
            "state": Finding.ACTIVE,
            "resource_name": resource_name,
            "category": "MEDIUM_RISK_ONE",
            "source_properties": {"s_value": str_value, "n_value": num_value},
            "event_time": now_proto,
        },
    )
    print(created_finding)
    # [END create_finding_with_properties]


def test_update_finding(source_name):
    # [START update_finding]
    from google.cloud import securitycenter as securitycenter
    from google.protobuf.struct_pb2 import Value
    from google.protobuf import field_mask_pb2
    from google.protobuf.timestamp_pb2 import Timestamp

    client = securitycenter.SecurityCenterClient()
    # Only update the specific source property and event_time.  event_time
    # is required for updates.
    field_mask = field_mask_pb2.FieldMask(
        paths=["source_properties.s_value", "event_time"]
    )
    value = Value()
    value.string_value = "new_string"

    # Set the update time to Now.  This must be some time greater then the
    # event_time on the original finding.
    now_proto = Timestamp()
    now_proto.GetCurrentTime()

    # source_name is the resource path for a source that has been
    # created previously (you can use list_sources to find a specific one).
    # Its format is:
    # source_name = "organizations/{organization_id}/sources/{source_id}"
    # e.g.:
    # source_name = "organizations/111122222444/sources/1234"
    finding_name = "{}/findings/samplefindingid2".format(source_name)
    updated_finding = client.update_finding(
        {
            "name": finding_name,
            "source_properties": {"s_value": value},
            "event_time": now_proto,
        },
        update_mask=field_mask,
    )

    print(
        "New Source properties: {}, Event Time {}".format(
            updated_finding.source_properties, updated_finding.event_time.ToDatetime()
        )
    )
    # [END update_finding]


def test_update_finding_state(source_name):
    """Demonstrate updating only a finding state."""
    # [START update_finding_state]
    from google.cloud import securitycenter as securitycenter
    from google.cloud.securitycenter_v1.proto.finding_pb2 import Finding
    from google.protobuf.timestamp_pb2 import Timestamp
    from datetime import datetime

    # Create a client.
    client = securitycenter.SecurityCenterClient()
    # source_name is the resource path for a source that has been
    # created previously (you can use list_sources to find a specific one).
    # Its format is:
    # source_name = "organizations/{organization_id}/sources/{source_id}"
    # e.g.:
    # source_name = "organizations/111122222444/sources/1234"
    finding_name = "{}/findings/samplefindingid2".format(source_name)

    now_proto = Timestamp()
    now_proto.GetCurrentTime()

    # Call the API to change the finding state to inactive as of now.
    new_finding = client.set_finding_state(
        finding_name, Finding.INACTIVE, start_time=now_proto
    )
    print("New state: {}".format(Finding.State.Name(new_finding.state)))
    # [END update_finding_state]


def test_trouble_shoot(source_name):
    """Demonstrate calling test_iam_permissions to determine if the 
    service account has the correct permisions."""
    # [START test_iam_permissions]
    from google.cloud import securitycenter as securitycenter

    # Create a client.
    client = securitycenter.SecurityCenterClient()
    # source_name is the resource path for a source that has been
    # created previously (you can use list_sources to find a specific one).
    # Its format is:
    # source_name = "organizations/{organization_id}/sources/{source_id}"
    # e.g.:
    # source_name = "organizations/111122222444/sources/1234"

    # Check for permssions to call create_finding or update_finding.
    permission_response = client.test_iam_permissions(
        source_name, ["securitycenter.findings.update"]
    )

    print(
        "Permision to create or update findings? {}".format(
            len(permission_response.permissions) > 0
        )
    )
    # [END test_iam_permissions]
    assert len(permission_response.permissions) > 0
    # [START test_iam_permissions]
    # Check for permissions necessary to call set_finding_state.
    permission_response = client.test_iam_permissions(
        source_name, ["securitycenter.findings.setState"]
    )
    print(
        "Permision to update state? {}".format(len(permission_response.permissions) > 0)
    )
    # [END test_iam_permissions]
    assert len(permission_response.permissions) > 0


def test_list_all_findings(organization_id):
    # [START list_all_findings]
    from google.cloud import securitycenter as securitycenter

    # Create a client.
    client = securitycenter.SecurityCenterClient()

    # organization_id is the numeric ID of the organization. e.g.:
    # organization_id = "111122222444"
    org_name = "organizations/{org_id}".format(org_id=organization_id)
    # The "sources/-" suffix lists findings across all sources.  You
    # also use a specific source_name instead.
    all_sources = "{org_name}/sources/-".format(org_name=org_name)
    for i, finding_result in enumerate(client.list_findings(all_sources)):
        print(
            "{}: name: {} resource: {}".format(
                i, finding_result.finding.name, finding_result.finding.resource_name
            )
        )
    # [END list_all_findings]
    assert i > 0


def test_list_filtered_findings(source_name):
    # [START list_filtered_findings]
    from google.cloud import securitycenter as securitycenter

    # Create a new client.
    client = securitycenter.SecurityCenterClient()

    # source_name is the resource path for a source that has been
    # created previously (you can use list_sources to find a specific one).
    # Its format is:
    # source_name = "organizations/{organization_id}/sources/{source_id}"
    # e.g.:
    # source_name = "organizations/111122222444/sources/1234"
    # You an also use a wild-card "-" for all sources:
    #   source_name = "organizations/111122222444/sources/-"
    finding_result_iterator = client.list_findings(
        source_name, filter_='category="MEDIUM_RISK_ONE"'
    )
    # Iterate an print all finding names and the resource they are
    # in reference to.
    for i, finding_result in enumerate(finding_result_iterator):
        print(
            "{}: name: {} resource: {}".format(
                i, finding_result.finding.name, finding_result.finding.resource_name
            )
        )
    # [END list_filtered_findings]
    assert i > 0


def test_list_findings_at_time(source_name):
    # [START list_findings_at_a_time]
    from google.cloud import securitycenter as securitycenter
    from google.protobuf.timestamp_pb2 import Timestamp
    from datetime import timedelta, datetime

    # Create a new client.
    client = securitycenter.SecurityCenterClient()

    # source_name is the resource path for a source that has been
    # created previously (you can use list_sources to find a specific one).
    # Its format is:
    # source_name = "organizations/{organization_id}/sources/{source_id}"
    # e.g.:
    # source_name = "organizations/111122222444/sources/1234"
    # You an also use a wild-card "-" for all sources:
    #   source_name = "organizations/111122222444/sources/-"
    five_days_ago = Timestamp()
    five_days_ago.FromDatetime(datetime.now() - timedelta(days=5))
    # [END list_findings_at_a_time]
    i = -1
    five_days_ago.FromDatetime(datetime(2019, 3, 5, 0, 0, 0))
    # [START list_findings_at_a_time]

    finding_result_iterator = client.list_findings(source_name, read_time=five_days_ago)
    for i, finding_result in enumerate(finding_result_iterator):
        print(
            "{}: name: {} resource: {}".format(
                i, finding_result.finding.name, finding_result.finding.resource_name
            )
        )
    # [END list_findings_at_a_time]
    assert i == -1