all: publish

latest.zip: .venv
	. .venv/bin/activate; python3 -m srodawlkp_gtfs

.venv: .venv/touchfile

.venv/touchfile: requirements.txt
	test -d venv || python3 -m venv .venv
	. .venv/bin/activate; pip install -Ur requirements.txt
	touch .venv/touchfile

clean:
	rm -rf _impuls_workspace
	rm latest.zip
	rm -rf out

publish: out/latest.zip

out/latest.zip: latest.zip
	mkdir -p out
	cp latest.zip out/latest.zip
	
