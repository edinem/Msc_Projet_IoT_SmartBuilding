.ONESHELL:

sources := backend.py
ozw_artifacts := options.xml ozwcache_*.xml *.log pyozw.sqlite zwscene.xml
py_artifacts := __pycache__/
git_artifacts := .git*
lab_artifacts := labo-setup/
py_files := $(wildcard *.py)
pi4_img_file := raspbian.img
img_mnt_root := /mnt/raspbian

.PHONY: help

all: help

pycheck: $(py_files)
	python -m py_compile $?

# ensure symlinks are local to the source directory
_slink:
	dname=$(dir $(slink))
	lname=$(notdir $(slink))
	pushd $$dname >/dev/null
	ln -sf $$lname.$(suffix) $$lname
	popd >/dev/null

incomplete: $(sources)
	$(MAKE) suffix=incomplete _slink slink=$<
labo: incomplete

unlock:
	git-crypt unlock

complete: $(sources)
	$(MAKE) suffix=complete _slink slink=$<

solution: complete

RUSER := pi
RHOST := rbpiw1
RPATH := /home/pi/IoT/Smart-Building
# echo -e "$(addsuffix complete,$(sources))\n$(ozw_artifacts)\n$(py_artifacts)\n$(git_artifacts)"
deploy: complete pycheck
	# use a subshell to correctly see the last newline. Rsync exclude is
	# handeled via STDIN
	(cat | rsync -CaLhv --exclude-from=- ./ $(RUSER)@$(RHOST):$(RPATH)) <<EOT
	$(addsuffix .complete,$(sources))
	$(addsuffix .incomplete,$(sources))
	$(ozw_artifacts)
	$(py_artifacts)
	$(git_artifacts)
	$(lab_artifacts)
	EOT

clean:
	rm -rf $(ozw_artifacts) __pycache__/

reset: clean incomplete
	# No-op


# mount an already *installed* Raspberry Pi OS. Normally, 2 partitions should
# be found -- there's no way of having losetup telling which (sub) loopdev are
# associated to the partitions...
mount-img:
	sudo mkdir -p $(img_mnt_root)/{boot,sys}
	sudo losetup -P /dev/loop0 $(pi4_img_file)
	sudo mount /dev/loop0p1 $(img_mnt_root)/boot
	sudo mount /dev/loop0p2 $(img_mnt_root)/sys

umount-img:
	sudo umount $(img_mnt_root)/boot
	sudo umount $(img_mnt_root)/sys
	sudo losetup -D

define _help_msg :=
Usage:

  make [target]

Targets:

  clean         remove build artifacts and specious files & dirs
  complete      prepare the source code for the 'solution' build
  deploy        deploy the (complete) app to "$(RHOST):$(RPATH)"
  help          guess what ;-)
  incomplete    prepare the source code for the 'labo' build
  labo          alias => 'incomplete'
  solution      alias => 'complete'
  uninstall     remove whatever app build from device
  unlock        decrypt sensitive files
  mount-img     mount an already installed Raspberry Pi OS image. Default
                file: pi4_img_file=$(pi4_img_file)
                (needs root privileges)
  umount-img    unmount a mounted Raspberry Pi OS image (needs root privileges)
endef

# the shell no-op silences 'nothing to be done...' messages
help:
	@: $(info $(_help_msg))
