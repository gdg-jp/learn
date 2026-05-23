# Build claat codelabs from markdown sources.
#
# claat exports to a directory named after the codelab `id` field, so we
# rename to a stable directory name afterwards. We also swap the remote
# claat-public asset URLs for a local libs/ copy and run the postfix
# script that escapes inline <code> spans containing raw HTML tags.

CLAAT  ?= claat
PYTHON ?= python3
MARP   ?= npx --yes -p @marp-team/marp-cli@latest marp

POSTFIX  := .claat/fix-claat-codespans.py
SLIDE_POSTFIX := .marp/fix-slide-html.py
LIBS_SRC ?= portfolio-2025/libs

# Marp theme. Slides can live in any directory; pass the path via INPUT=.
MARP_THEME := .marp/gdg.css
OUTPUT     ?= $(INPUT:.md=.html)

ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
%:
	@:

.PHONY: claat slide slide-pdf index

# Export a claat codelab. Usage:
#   make claat <content-name>
#   (source: <content-name>/claat.md, output: <content-name>/)
claat:
	@DIR=$(word 1,$(ARGS)); \
	if [ -z "$$DIR" ]; then \
	  echo "Usage: make claat <content-name>"; \
	  exit 2; \
	fi; \
	MD="$$DIR/claat.md"; OUT="$$DIR"; \
	TMPDIR=$$(mktemp -d); \
	$(CLAAT) export -o "$$TMPDIR" "$$MD"; \
	EXPORTED=$$(ls "$$TMPDIR"); \
	mkdir -p "$$OUT"; \
	cp -R "$$TMPDIR/$$EXPORTED"/. "$$OUT/"; \
	rm -rf "$$TMPDIR"; \
	rm -rf "$$OUT/libs"; \
	cp -R "$(LIBS_SRC)" "$$OUT/libs"; \
	sed -i '' 's|https://storage.googleapis.com/claat-public/|libs/|g' "$$OUT/index.html"; \
	$(PYTHON) $(POSTFIX) --source-md "$$MD" "$$OUT/index.html"; \
	$(PYTHON) scripts/gen-index.py

# Render a Marp deck. Usage:
#   make slide <content-name>
#   (source: <content-name>/slide.md, output: <content-name>/slide/index.html)
#
# Also renders the first slide as an OGP image (<content-name>/slide/ogp.png).
slide:
	@if [ -z "$(ARGS)" ]; then \
	  echo "Usage: make slide <content-name>"; \
	  exit 2; \
	fi
	@DIR="$(word 1,$(ARGS))"; \
	SRC="$$DIR/slide.md"; \
	OUT="$$DIR/slide/index.html"; \
	OGP="$$DIR/slide/ogp.png"; \
	$(MARP) --theme-set $(MARP_THEME) --html "$$SRC" -o "$$OUT"; \
	$(MARP) --theme-set $(MARP_THEME) --html --allow-local-files --image png "$$SRC" -o "$$OGP"; \
	$(PYTHON) $(SLIDE_POSTFIX) "$$OUT"; \
	$(PYTHON) scripts/gen-index.py

# Export a Marp deck to PDF. Usage:
#   make slide-pdf path/to/deck.md [path/to/deck.pdf]
slide-pdf:
	@if [ -z "$(ARGS)" ]; then \
	  echo "Usage: make slide-pdf path/to/deck.md [path/to/deck.pdf]"; \
	  exit 2; \
	fi
	$(MARP) --theme-set $(MARP_THEME) --html --pdf --allow-local-files "$(word 1,$(ARGS))" -o "$(if $(word 2,$(ARGS)),$(word 2,$(ARGS)),$(patsubst %.md,%.pdf,$(word 1,$(ARGS))))"

# Regenerate the root index.html resource listing.
#   make index
index:
	$(PYTHON) scripts/gen-index.py
