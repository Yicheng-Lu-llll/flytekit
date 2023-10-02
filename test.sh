git add .
git commit -s -m "test"
git push

pip install -U git+https://github.com/Yicheng-Lu-llll/flytekit.git@"ray-agent#egg=flytekitplugins-ray&subdirectory=plugins/flytekit-ray" # replace with your own repo and branch
pip install -U git+https://github.com/Yicheng-Lu-llll/flytekit.git@ray-agent
