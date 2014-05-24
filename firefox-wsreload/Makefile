# Firefox WSReload XPI Makefile
# http://github.com/martinec/wsreload/firefox-wsreload
# This make script is based in the Password Alerts addon Makefile
# http://github.com/mozilla/watchdog-alert-passwords/blob/master/Makefile

# Source directory
ifeq ($(SOURCE_DIR),)
  export SOURCE_DIR = $(shell pwd)
endif

# Firefox profile directory
ifneq ($(PROFILE_DIR),)
  PROFILE_DIR := --profiledir="$(FIREFOX_PROFILE)"
endif

# Git command
GIT_BIN				:= git

# addon-sdk git url
SDK_GIT_URL   := https://github.com/mozilla/addon-sdk.git

# addon-sdk directory
ifeq ($(SDK_DIR),)
	SDK_DIR    := $(SOURCE_DIR)/addon-sdk
endif

# addon-sdk binary directory
SDK_BIN_DIR  := $(SDK_DIR)/bin

# addon-sdk cfx tool
CFX_BIN      := $(SDK_BIN_DIR)/cfx

# Firefox command
ifneq ($(FIREFOX_BIN),)
 FIREFOX_BIN := -b "$(FIREFOX_BIN)"
endif

# addon-sdk cfx tool arguments
CFX_BIN_ARGS := $(FIREFOX_BIN) $(PROFILE_DIR) --binary-args="-console -purgecaches"

all: xpi

xpi: pull
	@$(CFX_BIN) xpi $(CFX_BIN_ARGS)

pull:
	@mkdir -p $(SDK_DIR)
	@if [ -e $(CFX_BIN) ]; then 					 \
		cd $(SDK_DIR) ;                      \
		$(GIT_BIN) pull ;                    \
	 else                              		 \
		cd $(SDK_DIR) ;                      \
		$(GIT_BIN) clone $(SDK_GIT_URL) . ;  \
		fi;
	@cd $(SOURCE_DIR)

test: pull
	@$(CFX_BIN) test -v $(CFX_BIN_ARGS)

run: pull
	@$(CFX_BIN) run $(CFX_BIN_ARGS)

clean:
	@rm *.xpi

.PHONY: xpi test run