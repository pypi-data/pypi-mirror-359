import json
import os
import re
import socket

import typer
from IPy import IP
from rich.console import Console
from rich.progress import track
from typing_extensions import Annotated

console = Console()


def validate_ports_input(ports: str) -> list:
    single_pattern = r"^\d$"
    dash_pattern = r"^\d+\-\d+$"
    comma_pattern = r"^\d+(\,\d+)*$"
    if re.match(single_pattern, ports):
        parsed_ports = [int(ports)]
    if re.match(dash_pattern, ports):
        ports_range = ports.split("-")
        parsed_ports = list(range(int(ports_range[0]), int(ports_range[1])))
    elif re.match(comma_pattern, ports):
        ports_specific = ports.split(",")
        parsed_ports = [int(port) for port in ports_specific]
    else:
        raise Exception(f"'{ports}' is not a valid pattern for ports option")
    return parsed_ports


def check_ip(target: str) -> str:
    try:
        return IP(target)
    except ValueError:
        return socket.gethostbyname(target)


def ping_target(ip: str) -> bool:
    param = "-n" if os.sys.platform.lower() == "win32" else "-c"
    null_output = (
        ">nul 2>&1" if os.sys.platform.lower() == "win32" else "> /dev/null 2>&1"
    )
    response = os.system(f"ping {param} 1 {ip} {null_output}")

    # and then check the response...
    if response == 0:
        return True
    else:
        return False


def scan_ports(ip: str, ports: list) -> list:
    ports_info = []
    dict_tmp = {
        "port_number": "",
        "active": False,
        "service": "",
    }
    sock = socket.socket()
    sock.settimeout(0.5)
    # console.print(f"Ports being scanned {ports}")
    for port in track(ports, description="Scanning ports..."):
        # console.print(f"Ports being scanned {port}")
        try:
            sock.connect((ip, port))
            # console.print(f"Port number {port} open")
            dict_tmp["port_number"] = port
            dict_tmp["active"] = True

        except Exception:
            # console.print(f"Couldn't connect to port {port}")
            continue
        try:
            banner = sock.recv(1024).decode().strip("\n").strip("\r")
            # console.print(f"Banner: {banner}")
            dict_tmp["service"] = banner
            # console.print(f"Dict: {dict_tmp}")
            sock.close()
            ports_info.append(dict_tmp)
        except:
            dict_tmp["service"] = "No Information Found"
            ports_info.append(dict_tmp)
    return ports_info


# Main Network Scan Command
def network_scanner(
    target: Annotated[
        str,
        typer.Argument(
            help="Chose a target (IP, IP range or Network).",
        ),
    ],
    ports: Annotated[
        str,
        typer.Option(
            "--ports",
            "-p",
            help="You can chose a specific port (ex.: 22 will scan port 22), an interval of ports separated by '-' (ex.: 0-23) and specific ports separated by ',' (ex.: 22,443).",
        ),
    ] = "",
    wk_ports: Annotated[
        bool,
        typer.Option(
            "--wk-ports",
            "-wkp",
            help="Scan all well known ports (0-1023).",
        ),
    ] = False,
    registered_ports: Annotated[
        bool,
        typer.Option(
            "--registered-ports",
            "-rp",
            help="Scan all registered ports (1024-49151).",
        ),
    ] = False,
    all_ports: Annotated[
        bool,
        typer.Option(
            "--all-ports",
            "-ap",
            help="Scan all 65535 ports available.",
        ),
    ] = False,
    ping_bypass: Annotated[
        bool,
        typer.Option(
            "--ping-bypass",
            "-pB",
            help="Bypass the ping analysis.",
        ),
    ] = False,
    report_path: Annotated[
        str,
        typer.Option(
            "--report-path",
            "-R",
            help="Receive a human readable report from network-scanner. To use this option you need to supply a valid path. (Ex.: -R /some/folder)",
        ),
    ] = "",
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Choose a different output path for json file.",
        ),
    ] = "",
):
    ips = check_ip(target)

    console.print(f"Targeting: {target}")

    report = []

    for ip in ips:
        ip_str = ip.strNormal()
        ip_info = {"target": ip_str, "ports": ""}

        if not ping_bypass:
            if not ping_target(ip_str):
                console.print(f"{ip} is down!")
                continue
            console.print(f"{ip} is up!")
        if wk_ports:
            port_list = list(range(0, 1023 + 1))
            ports_info = scan_ports(ip_str, port_list)
        elif registered_ports:
            port_list = list(range(1024, 49151 + 1))
            ports_info = scan_ports(ip_str, port_list)
        elif all_ports:
            port_list = list(range(0, 65535 + 1))
            ports_info = scan_ports(ip_str, port_list)
        elif ports:
            ports_parsed = validate_ports_input(ports)
            ports_info = scan_ports(ip_str, ports_parsed)
        else:
            raise Exception(
                "You have to choose a port option (--ports, --wk-ports, --registered-ports, --all-ports), check --help for options description."
            )

        ip_info["ports"] = ports_info

        report.append(ip_info)

    console.print(f"Report: {report}")

    path_cwd = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )

    path_dir = path_cwd + "/reports"
    file_name = "/gh_network_scan_report.json"

    path_final = path_dir + file_name

    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    # console.print(f"Current path: {path_final}")

    with open(path_final, "w") as fp:
        json.dump(report, fp, indent=2)

    # if output:
    #     if not os.path.exists(output):
    #         os.makedirs(output)
    #     with open(output + file_name, "w") as fp:
    #         json.dump(report, fp, indent=2)

    # if report:
    #     if not os.path.exists(report):
    #         os.makedirs(report)
    # TODO: Call function that creates report from json
    # def gen_report(report, report_path)


"""
json example:

[
    {
        "target": "192.168.1.254",
        "ports": [
            { 
                "port_number": "22",
                "active": True, 
                "service": "sshd ubuntu ..."
                "vulnerability": [
                    {
                        "cve": "", 
                        "cvss": ""
                    }
                    {
                        "cve": "", 
                        "cvss": ""
                    }
                    {
                        "cve": "", 
                        "cvss": ""
                    }
                ]
            },
            {
                "port_number": "<port_number>": 
                "active": bool, 
                "service":  "<information_from_that_port>"
            }
        ],
    },
    {
        "target": "<some_ip>",
        "ports": [
            { 
                "port_number": "<some_port>",
                "active": bool, 
                "service": "<response_from_socket"
            }
        ],
    },
]
"""
