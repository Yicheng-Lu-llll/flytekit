export PATH=$PATH:~/.local/bin
export FLYTECTL_CONFIG=/root/.flyte/config-sandbox.yaml
export KUBECONFIG=$KUBECONFIG:/root/.kube/config:/root/.flyte/k3s/k3s.yaml


export FLYTE_INTERNAL_IMAGE="yichenglu/flytekit:test_visualization"

git add . && git commit -s -m "test" && git push origin testvisualization

docker build --no-cache -t  "${FLYTE_INTERNAL_IMAGE}" .
docker push ${FLYTE_INTERNAL_IMAGE}
pyflyte run --image ${FLYTE_INTERNAL_IMAGE} --remote ./test.py  wf


