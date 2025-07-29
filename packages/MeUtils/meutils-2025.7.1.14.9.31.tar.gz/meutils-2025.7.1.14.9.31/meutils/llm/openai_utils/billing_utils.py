#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : usage_utils
# @Time         : 2025/6/24 08:53
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
"""
1. 同步任务（流 非流）
    - 按次
    - 按量
2. 异步任务
    - 按次
    - 按量
"""

from contextlib import asynccontextmanager

from meutils.pipe import *
from meutils.llm.clients import AsyncOpenAI
from meutils.apis.utils import make_request

base_url = "https://api.chatfire.cn/flux/v1"


# base_url="http://110.42.51.201:38888/flux/v1"
# base_url = "http://0.0.0.0:8000/v1/async/flux/v1"
# base_url = "https://openai-dev.chatfire.cn/usage/async/flux/v1"

async def billing_for_async_task(
        model: str = "usage-async",
        task_id: str = "123456",
        n: float = 1,
        api_key: Optional[str] = None
):
    model = model.lower()  # 统一小写

    if n := int(np.round(n)):
        tasks = [
            make_request(
                base_url=base_url,
                api_key=api_key,
                path=f"/{model}",
                payload={
                    "id": task_id,
                    # 'polling_url': f'{base_url}/get_result?id={task_id}',
                }
            )
            for i in range(n)
        ]

        _ = await asyncio.gather(*tasks)
        return _


async def get_async_task(id: str = "123456"):
    # 计费
    _ = await make_request(
        base_url=base_url,
        path=f"/get_result?id={id}",

        method="GET"
    )

    return _


async def billing_for_tokens(
        model: str = "usage-chat",

        usage: Optional[dict] = None,

        api_key: Optional[str] = None,

        n: Optional[float] = None,  # 按次走以前逻辑也行
):
    """

    image_usage = {
            "input_tokens": input_tokens,
            "input_tokens_details": {
                "text_tokens": input_tokens,
                "image_tokens": 0,
            },
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }

            # usage = {
        #     "prompt_tokens": input_tokens,
        #     "completion_tokens": output_tokens,
        #     "total_tokens": total_tokens
        # }
    """
    usage = usage or {}
    n = n and int(np.round(n))

    client = AsyncOpenAI(api_key=api_key)
    if n:
        _ = await client.images.generate(
            model=model,
            prompt="ChatfireAPI",
            n=n
        )

    elif "input_tokens" in usage:
        _ = await client.images.generate(
            model=model,
            prompt="ChatfireAPI",
            n=n,
            extra_body={"extra_fields": usage}
        )
    else:
        _ = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "ChatfireAPI"}],
            extra_body={"extra_body": usage}
        )
    return _


def get_billing_n(request: Union[BaseModel, dict], duration: float = 6, resolution: float = 480):
    """继续拓展其兼容性
         MINIMAX_HAILUO_02_10S_768P
    :param request:
    :param duration:
    :return:
    """
    if isinstance(request, BaseModel):
        request = request.model_dump()

    # 数量
    num = request.get("n") or request.get("num_images") or 1

    # 时长
    dur = np.ceil(request.get("duration", duration) / duration)  # 默认 6s
    durs = {"--duration 10", "--dur 10"}
    if any(i in str(request) for i in durs):
        dur = max(dur, 2)

    # 分辨率 resolution 480p 720p 1080p
    rs = request.get("resolution", str(resolution)).lower().removesuffix('p')  # 默认 720p
    rs = np.ceil(int(rs) / resolution)  # 1 2 3
    rss = {"--resolution 1080p", "--rs 1080p"}
    if any(i in str(request) for i in rss):
        dur = max(rs, 2)

    return num * dur * rs or 1


@asynccontextmanager
async def billing_flow_for_async_task(
        model: str = "usage-async",
        task_id: str = "123456",
        n: float = 1,
        api_key: Optional[str] = None
):
    if n:  # 计费
        await billing_for_async_task(model, task_id=task_id, n=n, api_key=api_key)
        yield

    else:  # 不计费
        a = yield
        logger.debug(a)


@asynccontextmanager
async def billing_flow_for_tokens(
        model: str = "usage-chat",

        usage: Optional[dict] = None,  # None就是按次

        api_key: Optional[str] = None,
):
    await billing_for_tokens(model, usage=usage, api_key=api_key)

    yield


if __name__ == '__main__':
    # arun(create_usage_for_tokens())
    # usage = {
    #     "input_tokens": 1,
    #     "input_tokens_details": {
    #         "text_tokens": 1,
    #         "image_tokens": 0,
    #     },
    #     "output_tokens": 100,
    #     "total_tokens": 101
    # }
    # n = 1
    # arun(create_usage_for_tokens(usage=usage, n=n))

    # arun(create_usage_for_async_task(task_id="task_id", n=1))

    model = "usage-async"
    # model = "fal-ai/model1"
    task_id = f"{model}-{int(time.time())}"
    model = "doubao-seedance-1-0-pro-250528"

    # arun(billing_for_async_task(model, task_id=task_id, n=3))

    data = {
        "model": "doubao-seedance-1-0-pro-250528",
        "content": [
            {
                "type": "text",
                "text": "多个镜头。一名侦探进入一间光线昏暗的房间。他检查桌上的线索，手里拿起桌上的某个物品。镜头转向他正在思索。 --ratio 16:9"
            }
        ]
    }

    print(get_billing_n(data))

    #
    # arun(get_async_task(task_id))
    #
    # arun(get_async_task(f"{task_id}-Ready", status="Ready"))

    # arun(get_async_task('chatfire-123456-Ready-1'))

# {
#   "id": "chatfire-1750769977.856766",
#   "result": {},
#   "status": "Error",
#   "details": {
#     "xx": [
#       "xxxx"
#     ]
#   },
#   "progress": 99
# }
