#!/bin/bash

set -euo pipefail

#  Exit with the error if no argument is passed
if [[ $# -lt 1 ]]; then
  echo "You must specify at least 1 VM to provision"
  exit 1
fi

# Create an array called "vms" from the comma-separated arguments
IFS=',' read -ra vms <<< "$1"

# Create and start VMs in parallel using limactl
for vm in "${vms[@]}"; do
  (
    limactl create template:docker-rootful \
      --yes \
      --name "$vm" \
      --network lima:user-v2
    limactl start "$vm"
    echo "VM $vm is ready"
  ) &
done

wait

# List provisioned by Lima VMs
limactl ls
