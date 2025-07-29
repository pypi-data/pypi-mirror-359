# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from dynamo._core import AggregatedMetrics as AggregatedMetrics

try:
    from dynamo._core import BlockManager as BlockManager
except ImportError:
    pass  # BlockManager is not enabled by default

from dynamo._core import DisaggregatedRouter as DisaggregatedRouter
from dynamo._core import HttpAsyncEngine as HttpAsyncEngine
from dynamo._core import HttpError as HttpError
from dynamo._core import HttpService as HttpService
from dynamo._core import KvEventPublisher as KvEventPublisher
from dynamo._core import KvIndexer as KvIndexer
from dynamo._core import KvMetricsAggregator as KvMetricsAggregator
from dynamo._core import KvRecorder as KvRecorder
from dynamo._core import KvRouter as KvRouter
from dynamo._core import ModelType as ModelType
from dynamo._core import OverlapScores as OverlapScores
from dynamo._core import WorkerMetricsPublisher as WorkerMetricsPublisher
from dynamo._core import ZmqKvEventPublisher as ZmqKvEventPublisher
from dynamo._core import ZmqKvEventPublisherConfig as ZmqKvEventPublisherConfig
from dynamo._core import register_llm as register_llm

try:
    from dynamo.llm.tensorrtllm import (  # noqa: F401
        get_llm_engine as get_tensorrtllm_engine,
    )
    from dynamo.llm.tensorrtllm import (  # noqa: F401
        get_publisher as get_tensorrtllm_publisher,
    )
except ImportError:
    pass  # TensorRTLLM is not enabled by default
except Exception as e:
    # Don't let TensorRTLLM break other engines
    logger = logging.getLogger(__name__)
    logger.exception(f"Error importing TensorRT-LLM components: {e}")
