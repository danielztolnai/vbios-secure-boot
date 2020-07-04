COMMANDS := clean
MODULES := digest-to-efi-sig-list rom-parser

$(COMMANDS): $(MODULES)
$(MODULES):
	$(MAKE) -C $@ $(MAKECMDGOALS)

.PHONY: $(COMMANDS) $(MODULES)
