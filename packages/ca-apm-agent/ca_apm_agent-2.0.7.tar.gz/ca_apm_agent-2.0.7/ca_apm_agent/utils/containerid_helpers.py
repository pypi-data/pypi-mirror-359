__copyright__ = """
* Copyright (c) 2024 Broadcom. All rights reserved. The term "Broadcom"
* refers to Broadcom Inc. and/or its subsidiaries. All trademarks, trade
* names, service marks, and logos referenced herein belong to their
* respective companies.
*
* This software and all information contained therein is confidential and
* proprietary and shall not be duplicated, used, disclosed or disseminated
* in any way except as authorized by the applicable license agreement,
* without the express written permission of Broadcom. All authorized
* reproductions must be marked with this language.
*
* EXCEPT AS SET FORTH IN THE APPLICABLE LICENSE AGREEMENT, TO THE EXTENT
* PERMITTED BY APPLICABLE LAW OR AS AGREED BY BROADCOM IN ITS APPLICABLE
* LICENSE AGREEMENT, BROADCOM PROVIDES THIS DOCUMENTATION "AS IS" WITHOUT
* WARRANTY OF ANY KIND, INCLUDING WITHOUT LIMITATION, ANY IMPLIED
* WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
* NONINFRINGEMENT.  IN NO EVENT WILL BROADCOM BE LIABLE TO THE END USER OR
* ANY THIRD PARTY FOR ANY LOSS OR DAMAGE, DIRECT OR INDIRECT, FROM THE USE
* OF THIS DOCUMENTATION, INCLUDING WITHOUT LIMITATION, LOST PROFITS, LOST
* INVESTMENT, BUSINESS INTERRUPTION, GOODWILL, OR LOST DATA, EVEN IF
* BROADCOM IS EXPRESSLY ADVISED IN ADVANCE OF THE POSSIBILITY OF SUCH LOSS
* OR DAMAGE.
"""

import os
from ca_apm_agent.connections.constants import APMENV_INTROSCOPE_AGENT_POD_NAMESPACE, APMENV_INTROSCOPE_AGENT_POD_NAME, APMENV_INTROSCOPE_AGENT_POD_CONTAINER_NAME, APMENV_INTROSCOPE_AGENT_POD_IPADDRESS

environ = os.environ

def getPodName():
    podName = None
    if APMENV_INTROSCOPE_AGENT_POD_NAME in environ:
           podName = environ[APMENV_INTROSCOPE_AGENT_POD_NAME]
    else:
        if APMENV_INTROSCOPE_AGENT_POD_NAME.upper() in environ:
            podName = environ[APMENV_INTROSCOPE_AGENT_POD_NAME.upper()]

    return podName

def getPodNamespace():
    podNamespace = None
    if APMENV_INTROSCOPE_AGENT_POD_NAMESPACE in environ:
           podNamespace = environ[APMENV_INTROSCOPE_AGENT_POD_NAMESPACE]
    else:
        if APMENV_INTROSCOPE_AGENT_POD_NAMESPACE.upper() in environ:
            podNamespace = environ[APMENV_INTROSCOPE_AGENT_POD_NAMESPACE.upper()]

    return podNamespace

def getContainerName():
    containerName = None
    if APMENV_INTROSCOPE_AGENT_POD_CONTAINER_NAME in environ:
           containerName = environ[APMENV_INTROSCOPE_AGENT_POD_CONTAINER_NAME]
    else:
        if APMENV_INTROSCOPE_AGENT_POD_CONTAINER_NAME.upper() in environ:
            containerName = environ[APMENV_INTROSCOPE_AGENT_POD_CONTAINER_NAME.upper()]

    return containerName

def getPodIPAddress():
    podIpAddress = None
    if APMENV_INTROSCOPE_AGENT_POD_IPADDRESS in environ:
           podIpAddress = environ[APMENV_INTROSCOPE_AGENT_POD_IPADDRESS]
    else:
        if APMENV_INTROSCOPE_AGENT_POD_IPADDRESS.upper() in environ:
            podIpAddress = environ[APMENV_INTROSCOPE_AGENT_POD_IPADDRESS.upper()]

    return podIpAddress
    