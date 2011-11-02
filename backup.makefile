# Using make to synchronize my files
# BIDIRECTIONAL SYNCING
# With the benefit of backing up
# 
# Link it to Makefile in your home to use "make TARGET".
 
# 2009/08
# update 2009/09/09
# version 0.1b
# Remo Giermann

FILENAME:=~/bin/backup.makefile
VERSION:=0.1b
PUTTARGETS:=doc coding engineering 
GETTARGETS:=gdoc gcoding gengineering 
DELTARGETS:=Ddoc Dcoding Dengineering
REMOTE:=krypton
REMOTE_PREFIX:=/srv/mirror/mo
RSYNC:=/usr/bin/rsync
RSFLAGS:=-zaruv
RSDRYFLAGS:=--dry-run
RSDELFLAGS:=--delete 

# default rule
all: put

# sync sends updates, dotfiles and removes non-existent files on remote target
sync: delete dotfiles

delete: $(DELTARGETS)

get: $(GETTARGETS)

put: $(PUTTARGETS)

cd:
	cd ~

dotfiles:
	tar \
--exclude ~/.cache \
--exclude ~/.kde/share \
--exclude ~/.kde4/share \
--exclude ~/.thumbnails \
-czf /tmp/dotfiles-`hostname`-`date +%Y%m%d-%HH%M`.tgz ~/.[a-zA-Z0-9]*
	$(RSYNC) $(RSFLAGS) /tmp/dotfiles*.tgz $(REMOTE):$(REMOTE_PREFIX)/
	rm /tmp/dotfiles-`hostname`-*.tgz

list:
	@echo version: $(VERSION)
	@echo put targets: $(PUTTARGETS)
	@echo get targets: $(GETTARGETS)
	@echo delete targets: $(DELTARGETS)
	@echo remote: $(REMOTE)
	@echo remote prefix: $(REMOTE_PREFIX)
	@echo rsync: $(RSYNC) $(RSFLAGS)
	@echo rsync to delete: $(RSYNC) $(RSDELFLAGS) $(RSFLAGS)
	@echo rsync dry-run: $(RSYNC) $(RSDRYFLAGS) $(RSFLAGS)

# put doc/
doc: cd
	$(RSYNC) $(RSFLAGS) doc $(REMOTE):$(REMOTE_PREFIX)/
drydoc: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) doc $(REMOTE):$(REMOTE_PREFIX)/
# get doc/
gdoc: cd
	$(RSYNC) $(RSFLAGS) $(REMOTE):$(REMOTE_PREFIX)/doc .
drygdoc: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) $(REMOTE):$(REMOTE_PREFIX)/doc .
# delete non-existent files on remote in target doc/
Ddoc: cd
	$(RSYNC) $(RSFLAGS) $(RSDELFLAGS) doc $(REMOTE):$(REMOTE_PREFIX)/
dryDdoc: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) $(RSDELFLAGS) doc $(REMOTE):$(REMOTE_PREFIX)/

coding: cd
	$(RSYNC) $(RSFLAGS) coding $(REMOTE):$(REMOTE_PREFIX)/
gcoding: cd
	$(RSYNC) $(RSFLAGS) $(REMOTE):$(REMOTE_PREFIX)/coding .
Dcoding: cd
	$(RSYNC) $(RSFLAGS) $(RSDELFLAGS) coding $(REMOTE):$(REMOTE_PREFIX)/

drycoding: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) coding $(REMOTE):$(REMOTE_PREFIX)/
drygcoding: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) $(REMOTE):$(REMOTE_PREFIX)/coding .
dryDcoding: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) $(RSDELFLAGS) coding $(REMOTE):$(REMOTE_PREFIX)/

engineering: cd
	$(RSYNC) $(RSFLAGS) engineering $(REMOTE):$(REMOTE_PREFIX)/
gengineering: cd
	$(RSYNC) $(RSFLAGS) $(REMOTE):$(REMOTE_PREFIX)/engineering .
Dengineering: cd
	$(RSYNC) $(RSFLAGS) $(RSDELFLAGS) engineering $(REMOTE):$(REMOTE_PREFIX)/

dryengineering: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) engineering $(REMOTE):$(REMOTE_PREFIX)/
drygengineering: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) $(REMOTE):$(REMOTE_PREFIX)/engineering .
dryDengineering: cd
	$(RSYNC) $(RSDRYFLAGS) $(RSFLAGS) $(RSDELFLAGS) engineering $(REMOTE):$(REMOTE_PREFIX)/
