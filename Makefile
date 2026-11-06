.PHONY: test doctor web cli audit release

test:
	python3 -m unittest discover -s tests -v

doctor:
	python3 dsant.py doctor

web:
	python3 -m sagaz --web

cli:
	python3 -m sagaz

audit:
	python3 tools/audit_bytes.py --strict

release: test audit
	python3 tools/pack_release.py
