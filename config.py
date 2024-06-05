#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "3a762fca-0a52-45ac-bee0-0965db163387")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "-j-8Q~Fko2fD2uiDYdGZByCcvDCm2zqWue3zxdeT")
    EXPIRE_AFTER_SECONDS = os.environ.get("ExpireAfterSeconds", 300)
