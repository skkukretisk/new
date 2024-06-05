#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "dec529fb-85bb-442c-8f47-e57f6fc50e6a")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "LZQ8Q~K3msg3xWaExWIxiUddAsDK4kRKg_wk1aHV")
    EXPIRE_AFTER_SECONDS = os.environ.get("ExpireAfterSeconds", 300)
