#!/usr/bin/env bash
# Resize the thesisos-dev boot disk and grow the Linux filesystem.
#
# Part 1 (GCP API) requires Compute Admin on your user account — run from Mac
# or Cloud Shell, NOT from inside the VM (the VM service account lacks
# compute.disks.resize).
#
# Usage:
#   # From Mac / Cloud Shell — set target size in GB:
#   DISK_GB=100 bash infra/dev-vm/resize-disk.sh gcp
#
#   # On the VM (after gcp step), expand partition + filesystem:
#   bash infra/dev-vm/resize-disk.sh os
#
#   # Or both in one go from Mac (SSH growpart over gcloud):
#   DISK_GB=100 bash infra/dev-vm/resize-disk.sh all
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-thesisos-prod}"
ZONE="${ZONE:-europe-west1-b}"
VM_NAME="${VM_NAME:-thesisos-dev}"
DISK_GB="${DISK_GB:-100}"
DISK_DEVICE="${DISK_DEVICE:-/dev/sda}"
PART_NUM="${PART_NUM:-1}"

resize_gcp() {
  echo "==> Resizing disk ${VM_NAME} to ${DISK_GB}GB (${ZONE}, ${PROJECT_ID})"
  gcloud config set project "$PROJECT_ID" >/dev/null
  gcloud compute disks resize "$VM_NAME" \
    --size="${DISK_GB}GB" \
    --zone="$ZONE" \
    --quiet
  echo "==> GCP disk resize requested. Current size:"
  gcloud compute disks describe "$VM_NAME" --zone="$ZONE" \
    --format='value(sizeGb)'
}

resize_os() {
  local part="${DISK_DEVICE}${PART_NUM}"
  echo "==> Before:"
  df -h /
  lsblk "$DISK_DEVICE"
  echo "==> Growing partition ${PART_NUM} on ${DISK_DEVICE}"
  sudo growpart "$DISK_DEVICE" "$PART_NUM"
  echo "==> Growing ext4 on ${part}"
  sudo resize2fs "$part"
  echo "==> After:"
  df -h /
  lsblk "$DISK_DEVICE"
}

case "${1:-}" in
  gcp) resize_gcp ;;
  os)  resize_os ;;
  all)
    resize_gcp
    echo "==> SSH into VM and expanding filesystem..."
    gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command \
      "sudo growpart ${DISK_DEVICE} ${PART_NUM} && sudo resize2fs ${DISK_DEVICE}${PART_NUM} && df -h /"
    ;;
  *)
    echo "Usage: DISK_GB=100 $0 {gcp|os|all}" >&2
    exit 1
    ;;
esac
