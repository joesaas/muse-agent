.PHONY: test demo run
test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
demo:
	PYTHONPATH=src python3 -m muse_agent --home /tmp/muse-agent-demo demo
run:
	PYTHONPATH=src python3 -m muse_agent --home /tmp/muse-agent-demo run "你好"
