#!/bin/bash

set -eo pipefail

MINIKUBE_IP="192.168.39.31"

case "$1" in
deploy)
  F_ARGS="deploy"
  T_ARGS="create"
  ;;
update)
  F_ARGS="update"
  T_ARGS="update"
  ;;
*)
  echo "use: $0 (deploy|update)"
  exit 1
  ;;
esac

deploy_function() {
    F_PREFIX="$1"
    F_POSTFIX="$2"
    F_NAME="$F_PREFIX-$F_POSTFIX"
    F_CALL="$3"
    kubeless function $F_ARGS $F_NAME --runtime python3.7 --from-file $F_PREFIX/handler.py --handler handler.$F_CALL --dependencies $F_PREFIX/requirements.txt
    kubeless trigger http $T_ARGS $F_NAME --function-name $F_NAME --hostname "faas.${MINIKUBE_IP}.nip.io" --path $F_PREFIX/$F_POSTFIX
}

deploy_function customers    get    get_customer
deploy_function customers    get-by get_customer_by
deploy_function customers    create create_customer
deploy_function customers    delete delete_customer
deploy_function transactions create create_transaction
deploy_function transactions list   list_transactions
deploy_function reports      get    get_report

