"""
Support for semver, graphviz and other modules which written for avoiding repetitive code.
"""
import graphviz
from packaging import version
from modules import constants, graph_functions, status, version_functions, kernel_version

VULNERABILITY = 'CVE-2022-0847'
DESCRIPTION = f'''{VULNERABILITY} - Dirty Pipe

CVSS Score: 7.8
NVD Link: https://nvd.nist.gov/vuln/detail/CVE-2022-0847

Linux Kernel bug in the PIPE mechanism due to missing initialization of the `flags` member in the 
`pipe_buffer` struct. The bug allows an attacker to create an unprivileged process that will inject code into a root 
process, and through doing so, escalate privileges by getting write permissions to read-only files. This can also be 
used in order to modify files in container images on the host, effectively poisoning any new containers based on the 
modified image.

Related Links:
https://www.rezilion.com/blog/dirty-pipe-what-you-need-to-know/
https://dirtypipe.cm4all.com/
https://blog.malwarebytes.com/exploits-and-vulnerabilities/2022/03/linux-dirty-pipe-vulnerability-gives-unprivileged-users-root-access/
'''
FIXED_KERNEL_VERSIONS = {'Debian unstable': '6.0.7-1', 'Debian 12': '6.0.5-1', 'Debian 11': '5.10.140-1',
                         'Debian 10': '4.19.249-2', 'Ubuntu 21.10': '5.13.0-35.40'}
FIXED_AWS_KERNEL_VERSIONS = {'Ubuntu 21.10': '5.13.0-1017.19'}
REMEDIATION = f'Upgrade kernel versions to:{FIXED_KERNEL_VERSIONS} or if running on an EC2 instance update kernel ' \
              f'version to: {FIXED_AWS_KERNEL_VERSIONS} or higher'
MITIGATION = ''


def check_kernel_version(debug):
    """This function returns if the kernel version is affected."""
    fixed_kernel_versions = FIXED_KERNEL_VERSIONS
    if kernel_version.is_aws(debug):
        fixed_kernel_versions = FIXED_AWS_KERNEL_VERSIONS
    host_os_release = os_release.check_release(fixed_kernel_versions, debug, container_name)
    if host_os_release == constants.UNSUPPORTED or not host_os_release:
        return host_os_release
    if host_os_release in fixed_kernel_versions:
        fixed_kernel_version = fixed_kernel_versions[host_os_release]
        return kernel_version.check_kernel(MIN_KERNEL_VERSION, fixed_kernel_version, debug)
    return ''


def validate(debug, container_name):
    """This function validates if the host is vulnerable to CVE-2022-0847."""
    state = {}
    if not container_name:
        affected = check_kernel_version(debug)
        if affected == constants.UNSUPPORTED:
            state[VULNERABILITY] = status.not_determined(VULNERABILITY)
        elif affected:
            state[VULNERABILITY] = status.vulnerable(VULNERABILITY)
            status.remediation_mitigation(REMEDIATION, MITIGATION)
        else:
            state[VULNERABILITY] = status.not_vulnerable(VULNERABILITY)
    else:
        print(constants.FULL_EXPLANATION_MESSAGE.format('Containers are not affected by kernel vulnerabilities'))
        state[VULNERABILITY] = status.not_vulnerable(VULNERABILITY)
    return state


def validation_flow_chart():
    """This function creates a graph that shows the vulnerability validation process of CVE-2022-0847."""
    vulnerability_graph = graphviz.Digraph('G', filename=VULNERABILITY, format='png')
    graph_functions.graph_start(VULNERABILITY, vulnerability_graph)
    vulnerability_graph.edge('Is it Linux?', 'Is the kernel version affected?', label='Yes')
    vulnerability_graph.edge('Is it Linux?', 'Not Vulnerable', label='No')
    vulnerability_graph.edge('Is the kernel version affected?', 'Vulnerable', label='Yes')
    vulnerability_graph.edge('Is the kernel version affected?', 'Not Vulnerable', label='No')
    graph_functions.graph_end(vulnerability_graph)


def main(description, graph, debug, container_name):
    """This is the main function."""
    if description:
        print(f'\n{DESCRIPTION}')
    state = validate(debug, container_name)
    if graph:
        validation_flow_chart()
    return state
