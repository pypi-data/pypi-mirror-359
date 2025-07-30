"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import inspect
import json
import os
import tempfile
import time

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import context, profile
from hcs_core.ctxp.util import error_details
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.separator import Separator

import hcs_cli.support.profile as profile_support
from hcs_cli.cmds.dev.fs import jenkins_util, k8s_util, license_info
from hcs_cli.cmds.dev.fs.common import log
from hcs_cli.cmds.dev.fs.common.log import fail as fail
from hcs_cli.cmds.dev.fs.common.log import step as step
from hcs_cli.cmds.dev.fs.k8s_util import kubectl
from hcs_cli.service import org_service
from hcs_cli.support.exec_util import exec
from hcs_cli.support.template_util import with_template_file


def require_env(name):
    value = os.getenv(name)
    if not value:
        fail(f"Missing required environment variable: {name}")
    return value


@click.command()
@cli.org_id
@click.option("--interactive/--auto", "-i/-a", is_flag=True, default=True, help="Interactive mode.")
@click.option("--step", "-s", type=str, required=False, help="Steps to run. Default is all steps.")
def init(step: str, interactive: bool, **kwargs):
    """Initialize feature stack with common settings and infrastructure."""

    if interactive:
        deployment_config = _collect_deployment_config()
    else:
        deployment_config = None

    if step:
        _run_single_step(step)
    else:
        _prepare_k8s_config()
        _prepare_profile()
        _validate_fs_auth()
        _get_client_credential_from_k8s_and_update_profile()

        if deployment_config is None or "_common_init" in deployment_config:
            _update_mqtt()
            _restart_services()
            _reg_datacenter()
            _create_org_details()
            _create_org_location_mapping()
            _create_license_info()
            _touch_fs_to_avoid_recycle()
        else:
            log.info("Skipping common init.")
        if deployment_config is None or "_create_infra_azure" in deployment_config:
            _create_infra_azure()
        else:
            log.info("Skipping Azure infrastructure creation.")
        if deployment_config is None or "_create_infra_akka" in deployment_config:
            _create_infra_akka()
        else:
            log.info("Skipping Akka infrastructure creation.")

        log.good("Done")


def _collect_deployment_config():
    choices = [
        Choice(value="_common_init", enabled=True, name="Common Init (Org, Datacenter, License, MQTT, ...)"),
        Separator(),
        Choice(
            value="_create_infra_akka",
            enabled=True,
            name="Akka Pools (Provider, Edge, UAG, Dedicated/Floating/Multi-session)",
        ),
        Choice(
            value="_create_infra_azure",
            enabled=True,
            name="Azure Pools (Provider, Edge, UAG, Dedicated/Floating/Multi-session)",
        ),
        # Separator(),
    ]

    return inquirer.checkbox(
        message="Select deployment features:",
        choices=choices,
        instruction="(Use SPACE to toggle, ENTER to confirm)",
        transformer=lambda result: ", ".join(result),
    ).execute()


@step
def _touch_fs_to_avoid_recycle():
    namespace = require_env("FS_NAME")
    ns_json = kubectl(f"get namespace {namespace} -ojson", get_json=True)
    metadata = ns_json.get("metadata", {})
    # Update annotations
    annotations = metadata.setdefault("annotations", {})
    # Update labels
    labels = metadata.setdefault("labels", {})
    updated_at = time.strftime("%Y-%m-%d")
    annotations["updatedAt"] = updated_at
    labels["updatedAt"] = updated_at
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(ns_json, f)
        temp_path = f.name
    kubectl(f"apply -f {temp_path}")
    os.remove(temp_path)
    log.good(f"Namespace {namespace} 'updatedAt' set to {updated_at}, so it will not be recycled.")


def _run_single_step(name):
    name = name.lower().replace("-", "_")
    import hcs_cli.cmds.dev.fs.init as my_self

    steps = [
        obj
        for fn_name, obj in inspect.getmembers(my_self)
        if inspect.isfunction(obj) and fn_name.startswith("_") and fn_name not in ["_run_single_step", "init"]
    ]
    candidates = [f for f in steps if name in f.__name__.lower()]
    if not candidates:
        fail(f"No step found matching '{name}'.")
    elif len(candidates) > 1:
        fail(f"Multiple steps found matching '{name}': {[f.__name__ for f in candidates]}")
    else:
        candidates[0]()


@step
def _prepare_k8s_config():
    fs_name = require_env("FS_NAME")
    if not k8s_util.validate_kubectl_config(fs_name, raise_on_error=False):
        feature_stack_service = os.getenv("FEATURE_STACK_SERVICE")
        if feature_stack_service:
            jenkins_util.download_kubeconfig(feature_stack_service)
            k8s_util.validate_kubectl_config(fs_name, raise_on_error=True)
        else:
            fail(
                "Feature stack kubectl config is not set.\n"
                "Recovery options:\n"
                "  1. Provide FEATURE_STACK_SERVICE=<service-name> in .env file, to download kubeconfig from Jenkins feature stack pipeline.\n"
                f"  2. Or download and copy feature stack kubeconfig to ~/.kube/_fs_config\n"
            )


def _resolve_bundled_file_path(relative_path: str):
    current_file_path = os.path.abspath(__file__)
    base_path = os.path.dirname(current_file_path)
    return os.path.join(base_path, relative_path)


def _hcs(cmd: str, output_json=False):
    cmd = f"hcs --no-upgrade-check {cmd}"
    if output_json:
        output = exec(cmd).stdout
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            fail(f"Failed to parse JSON output from command '{cmd}': {e}\nOutput: {output}")
    else:
        return exec(cmd, inherit_output=True, logOnError=False, raise_on_error=True)


@step
def _create_infra_azure():
    azure_plan_path = _resolve_bundled_file_path("provided_files/azure.plan.yml")

    # use the following command to inspect the resolved file
    #   hcs plan resolve
    # or examine the finally resolved input after deployment:
    #   hcs plan input

    _hcs("plan apply -f " + azure_plan_path)

    # To get the output, use the following command:
    #   hcs plan output -d
    # or programatically
    details = _hcs("plan output --details", output_json=True)

    # store in context
    context.set("infra", details)

    # It can be retrieved from other modules when needed:
    # infra = context.get("infra")
    # print(json.dumps(infra['mySite'], indent=4))
    # print(json.dumps(infra['myProvider'], indent=4))

    log.good("Azure infrastructure set up.")


@step
def _create_infra_akka():
    infra_plan_path = _resolve_bundled_file_path("provided_files/akka.plan.yml")
    _hcs("plan apply -f " + infra_plan_path)
    log.good("Akka infrastructure set up.")


@step
def _create_license_info():
    license_info.createLicenseFeatures()
    log.good("License set up.")


@step
def _update_mqtt():
    with_template_file(
        "provided_files/mqtt-server-external.yaml",
        substitutions={r"(namespace:\s*)\S+": rf"\1{profile.name()}"},
        fn=lambda temp_file_path: kubectl(f"apply -f {temp_file_path}"),
        base_path=__file__,
    )

    ip_address = _retrieve_mqtt_server_ip_address("mqtt-server-external")

    with_template_file(
        "provided_files/mqtt-secret.yaml",
        substitutions={
            r"(namespace:\s*)\S+": rf"\1{profile.name()}",
            r'(mqtt\.server-host:\s*)".*?"': rf'\1"{ip_address}"',
        },
        fn=lambda temp_file_path: kubectl(f"apply -f {temp_file_path}"),
        base_path=__file__,
    )

    log.good("MQTT set up.")


def _retrieve_mqtt_server_ip_address(service_name, timeout=300, interval=5):
    start = time.time()
    while time.time() - start < timeout:
        result = kubectl(f"get service mqtt-server-external")
        output = result.stdout.strip().splitlines()

        if len(output) >= 2:
            header = output[0].split()
            values = output[1].split()

            ip_index = header.index("EXTERNAL-IP")
            external_ip = values[ip_index]

            if external_ip.lower() != "<pending>" and external_ip.lower() != "<none>":
                log.good(f"External IP found: {external_ip}")
                return external_ip

        print("[…] Waiting for External IP to be assigned...")
        time.sleep(interval)

    fail(f"Timed out waiting for External IP of service '{service_name}'")


@step
def _prepare_profile():
    name = require_env("FS_NAME")
    api_token = os.getenv("HCS_API_TOKEN")
    org_id = require_env("ORG_ID")
    if not profile.exists(name):
        log.info("Feature profile does not exist. Creating profile: " + name)
        data = profile_support.create_for_feature_stack(name)
        if not api_token:
            fail("HCS_API_TOKEN is missing. Specify it in .env file.")
        data["csp"]["orgId"] = org_id
        data["csp"]["apiToken"] = api_token
        profile.create(name, data, overwrite=False, auto_use=True)
    else:
        if profile.name() != name:
            log.warn("Switching to profile: " + name)
            profile.use(name)
        data = profile.current()
        _validate_fs_url(data.hcs.url)
        updated = False
        if data.csp.orgId != org_id:
            log.warn(
                f"Current profile orgId ({data.csp.orgId}) does not match provided orgId. Updating profile to use the specified orgId {org_id}."
            )
            data.csp.orgId = org_id
            updated = True
        if api_token and data.csp.apiToken != api_token:
            log.warn(
                f"Current profile apiToken ({data.csp.apiToken}) does not match provided apiToken. Updating profile to use the specified apiToken."
            )
            data.csp.apiToken = api_token
            updated = True
        if updated:
            profile.save()

        if not data.csp.orgId:
            fail(
                "Profile orgId is not set.\n"
                "Recovery:\n"
                "  1. Provide --org parameter to set orgId for the profile.\n"
                "  2. Or set orgId in the profile manually: 'hcs profile edit'\n"
            )
        if not data.csp.apiToken:
            fail(
                "Profile apiToken is not set.\n"
                "Recovery:\n"
                "  1. Provide --api-token parameter to set apiToken for the profile.\n"
                "  2. Or set apiToken in the profile manually: 'hcs profile edit'\n"
            )


@step
def _validate_fs_auth():
    try:
        org_service.datacenter.list()
        log.good("Auth to feature stack")
    except Exception as e:
        fail(
            "Failed to connect to feature stack. Check your profile settings.\n"
            f"  Profile name={profile.name()}\n"
            f"  Profile url={profile.current().hcs.url}\n\n"
            f"Recovery options:\n"
            f"  1. Check if the feature stack is running and accessible.\n"
            f"  2. Verify your API token and org ID in the profile.\n",
            e,
        )


def _validate_fs_url(url):
    # https://nanw.fs.devframe.cp.horizon.omnissa.com
    if url.endswith("/"):
        url = url[:-1]
    if not url.endswith(".fs.devframe.cp.horizon.omnissa.com"):
        fail(
            f"The current profile URL is not a feature stack.\n"
            f"  Profile name={profile.name()}\n"
            f"  Profile url={url}\n\n"
            f"Recovery options:\n"
            f"  1. Create a profile for feature stack: 'hcs profile init --feature-stack <fs-name>'\n"
            f"  2. Or switch to a feature stack profile 'hcs profile use'\n"
        )

    start = url.find("//")
    if start == -1:
        fail("Invalid feature stack URL format: missing '//'. url=" + url)
    start += 2
    end = url.find(".", start)
    if end == -1:
        fail("Invalid feature stack URL format: missing '.' after '//' in url=" + url)
    fs_name = url[start:end]

    log.good("Feature stack: " + fs_name)
    return fs_name


@step
def _get_client_credential_from_k8s_and_update_profile():
    from hcs_cli.cmds.dev.fs import credential_helper

    credential_helper.get_client_credential_from_k8s_and_update_profile()
    log.good("Profile updated with client credentials for internal services.")


@step
def _reg_datacenter():
    feature_stack_url = profile.current().hcs.url
    payload1 = {
        "geoLocation": {"coordinates": [-122.143936, 37.468319], "type": "Point"},
        "name": "feature-stack-dc",
        "locations": ["EU", "JP", "GB", "IE", "US"],
        "regions": [
            "westus2",
            "westus",
            "centralus",
            "eastus2",
            "eastus",
            "westus3",
            "northeurope",
            "francecentral",
            "francesouth",
            "germanynorth",
            "germanywestcentral",
            "norwaywest",
            "norwayeast",
            "swedencentral",
            "swedensouth",
            "switzerlandnorth",
            "switzerlandwest",
            "uaecentral",
            "uaenorth",
            "uksouth",
            "ukwest",
            "westeurope",
            "japaneast",
            "australiaeast",
            "centralindia",
            "eastasia",
            "italynorth",
            "israelcentral",
            "usgovvirginia",
            "usgovarizona",
            "usgovtexas",
            "chinanorth",
            "chinanorth2",
            "brazilsouth",
            "us-central1",
            "ap-south-1",
            "us-west-1",
            "us-west-2",
            "us-east-1",
        ],
        "providerRegions": {
            "aws": ["ap-south-1", "us-west-1", "us-west-2", "us-east-1"],
            "gcp": ["us-central1"],
            "azure": [
                "westus2",
                "westus",
                "centralus",
                "eastus2",
                "eastus",
                "westus3",
                "northeurope",
                "francecentral",
                "francesouth",
                "germanynorth",
                "germanywestcentral",
                "norwaywest",
                "norwayeast",
                "swedencentral",
                "swedensouth",
                "switzerlandnorth",
                "switzerlandwest",
                "uaecentral",
                "uaenorth",
                "uksouth",
                "ukwest",
                "westeurope",
                "japaneast",
                "australiaeast",
                "centralindia",
                "eastasia",
                "italynorth",
                "israelcentral",
                "usgovvirginia",
                "usgovarizona",
                "usgovtexas",
                "chinanorth",
                "chinanorth2",
                "brazilsouth",
            ],
        },
        "url": feature_stack_url,
        "edgeHubUrl": "https://horizonv2-em.devframe.cp.horizon.omnissa.com",
        "edgeHubRegionCode": "us",
        "dnsUris": [
            "/subscriptions/bfd75b0b-ffce-4cf4-b46b-ecf18410c410/resourceGroups/horizonv2-sg-dev/providers/Microsoft.Network/dnszones/featurestack.devframe.cp.horizon.omnissa.com"
        ],
        "vmHubs": [
            {
                "name": "default",
                "url": "https://dev1b-westus2-cp103a.azcp.horizon.omnissa.com",
                "uagAasFqdn": "https://int.reverseconnect.uag.azcp.horizon.vmware.com",
                "azureRegions": [
                    "westus2",
                    "westus",
                    "centralus",
                    "eastus2",
                    "eastus",
                    "westus3",
                    "northeurope",
                    "francecentral",
                    "francesouth",
                    "germanynorth",
                    "germanywestcentral",
                    "norwaywest",
                    "norwayeast",
                    "swedencentral",
                    "swedensouth",
                    "switzerlandnorth",
                    "switzerlandwest",
                    "uaecentral",
                    "uaenorth",
                    "uksouth",
                    "ukwest",
                    "westeurope",
                    "japaneast",
                    "australiaeast",
                    "centralindia",
                    "eastasia",
                    "italynorth",
                    "israelcentral",
                    "usgovvirginia",
                    "usgovarizona",
                    "usgovtexas",
                    "chinanorth",
                    "chinanorth2",
                    "brazilsouth",
                ],
                "awsRegions": ["ap-south-1", "us-west-1", "us-east-1", "us-west-2"],
                "gcpRegions": ["us-central1"],
                "vmHubGeoPoint": {"type": "Point", "coordinates": [-119.852, 47.233]},
                "privateLinkServiceIds": [
                    "/subscriptions/f8b96ec7-cf11-4ae2-ab75-9e7755a00594/resourceGroups/dev1_westus2/providers/Microsoft.Network/privateLinkServices/dev1b-westus2-cp103a-privatelink"
                ],
                "standByVMHubDetails": {
                    "privateLinkServiceIds": [
                        "/subscriptions/f8b96ec7-cf11-4ae2-ab75-9e7755a00594/resourceGroups/dev1_westus2/providers/Microsoft.Network/privateLinkServices/dev1b-westus2-cp103a-privatelink"
                    ]
                },
                "privateLinkServiceToUse": "PRIMARY",
            }
        ],
    }
    try:
        ret = org_service.datacenter.create(payload1)
        print(ret)
        log.good("Datacenter registered.")
    except Exception as e:
        if "already exists" in error_details(e):
            log.info("Datacenter already exists. Skipping creation.")
        else:
            raise


@step
def _create_org_details():
    payload2 = {
        "customerName": f"{require_env('FS_NAME')}-dev",
        "customerType": "INTERNAL",
        "orgId": require_env("ORG_ID"),
        "wsOneOrgId": "pseudo-ws1-org-id",
    }
    try:
        ret = org_service.details.create(payload2)
        print(ret)
        log.good("Org details created.")
    except Exception as e:
        if "already exist" in error_details(e):
            log.info("Org details already exist. Skipping creation.")
        else:
            raise


@step
def _create_org_location_mapping():
    payload3 = {"location": "US", "orgId": require_env("ORG_ID")}
    ret = org_service.orglocationmapping.create(payload3)
    print(ret)
    log.good("Org location mapping created.")


@step
def _restart_services():
    kubectl("rollout restart deployment portal-deployment")
    kubectl("rollout restart statefulset vmhub-statefulset")
    kubectl("rollout restart statefulset connection-service-statefulset")
    kubectl("rollout restart statefulset clouddriver-statefulset")
    kubectl("rollout restart deployment infra-vsphere-twin-deployment")
    log.good("Services restarted.")
