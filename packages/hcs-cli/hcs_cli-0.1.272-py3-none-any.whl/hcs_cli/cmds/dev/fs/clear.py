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
import os
import time

import click
import hcs_core.sglib.cli_options as cli
from dotenv import load_dotenv
from hcs_core.ctxp import profile, recent

import hcs_cli.support.profile as profile_support
from hcs_cli.cmds.dev.fs import jenkins_util, k8s_util, license_info
from hcs_cli.cmds.dev.fs.common import log
from hcs_cli.cmds.dev.fs.init import _hcs, _resolve_bundled_file_path
from hcs_cli.service import org_service
from hcs_cli.support.template_util import with_template_file

fail = log.fail


@click.command()
@cli.org_id
def clear(org: str, **kwargs):
    """Clear deployments on feature stack."""
    azure_plan_path = _resolve_bundled_file_path("provided_files/azure.plan.yml")
    _hcs("plan destroy -f " + azure_plan_path)
    akka_plan_path = _resolve_bundled_file_path("provided_files/akka.plan.yml")
    _hcs("plan destroy -f " + akka_plan_path)
