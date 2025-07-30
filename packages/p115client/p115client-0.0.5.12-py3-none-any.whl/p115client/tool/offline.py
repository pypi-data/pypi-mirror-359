#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__all__ = ["offline_iter", "offline_restart_iter"]
__doc__ = "这个模块提供了一些和离线下载有关的函数"

from asyncio import sleep as async_sleep
from collections.abc import AsyncIterator, Callable, Iterable, Iterator
from itertools import count
from time import sleep, time
from typing import overload, Literal

from iterutils import run_gen_step_iter, with_iter_next, Yield, YieldFrom
from p115client import check_response, P115Client, P115OpenClient


@overload
def offline_iter(
    client: str | P115Client | P115OpenClient, 
    /, 
    page_start: int = 1, 
    page_stop: int = -1, 
    cooldown: float = 0, 
    use_open_api: bool = False, 
    *, 
    async_: Literal[False] = False, 
    **request_kwargs, 
) -> Iterator[dict]:
    ...
@overload
def offline_iter(
    client: str | P115Client | P115OpenClient, 
    /, 
    page_start: int = 1, 
    page_stop: int = -1, 
    cooldown: float = 0, 
    use_open_api: bool = False, 
    *, 
    async_: Literal[True], 
    **request_kwargs, 
) -> AsyncIterator[dict]:
    ...
def offline_iter(
    client: str | P115Client | P115OpenClient, 
    /, 
    page_start: int = 1, 
    page_stop: int = -1, 
    cooldown: float = 0, 
    use_open_api: bool = False, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
) -> Iterator[dict] | AsyncIterator[dict]:
    """遍历任务列表，获取任务信息

    :param client: 115 客户端或 cookies
    :param page_start: 开始页数
    :param page_stop: 结束页数（不含），如果 <= 0，则不限
    :param cooldown: 接口调用冷却时间，单位：秒
    :param use_open_api: 是否使用 open api
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数

    :return: 迭代器，返回任务信息
    """
    if isinstance(client, str):
        client = P115Client(client, check_for_relogin=True)
    if page_start < 1:
        page_start = 1
    if page_stop > 0:
        pages: Iterable[int] = range(page_start, page_stop)
    else:
        pages = count(page_start)
    if not isinstance(client, P115Client):
        use_open_api = True
    def gen_step():
        if use_open_api:
            offline_list = client.offline_list_open
        else:
            offline_list = client.offline_list
        if cooldown > 0:
            do_sleep = async_sleep if async_ else sleep
        last_t: float = 0
        for page in pages:
            if last_t and (diff := last_t + cooldown - time()) > 0:
                yield do_sleep(diff)
            last_t = time()
            resp = yield offline_list(page, async_=async_, **request_kwargs)
            check_response(resp)
            if use_open_api:
                resp = resp["data"]
            tasks = resp["tasks"]
            if not tasks:
                break
            yield YieldFrom(resp["tasks"])
            if len(tasks) < 30 or page >= resp["page_count"]:
                break
    return run_gen_step_iter(gen_step, async_=async_)


@overload
def offline_restart_iter(
    client: str | P115Client, 
    /, 
    predicate: None | Callable[[dict], bool] = None, 
    *, 
    async_: Literal[False] = False, 
    **request_kwargs, 
) -> Iterator[dict]:
    ...
@overload
def offline_restart_iter(
    client: str | P115Client, 
    /, 
    predicate: None | Callable[[dict], bool] = None, 
    *, 
    async_: Literal[True], 
    **request_kwargs, 
) -> AsyncIterator[dict]:
    ...
def offline_restart_iter(
    client: str | P115Client, 
    /, 
    predicate: None | Callable[[dict], bool] = None, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
) -> Iterator[dict] | AsyncIterator[dict]:
    """重试任务：重试那些因为空间不足而转存失败的任务

    :param client: 115 客户端或 cookies
    :param predicate: 断言，用于筛选
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数

    :return: 迭代器，逐个任务返回执行重试后的响应
    """
    if isinstance(client, str):
        client = P115Client(client, check_for_relogin=True)
    def gen_step():
        left_no_space: list[dict] = []
        add_task = left_no_space.append
        with with_iter_next(offline_iter(
            client, 
            async_=async_, 
            **request_kwargs, 
        )) as do_next:
            while True:
                task = yield do_next()
                if task["move"] == -1:
                    add_task(task)
                elif task["status"] == 2:
                    break
        for task in filter(predicate, left_no_space):
            resp = yield client.offline_restart(
                task["info_hash"], 
                async_=async_, 
                **request_kwargs, 
            )
            resp["task"] = task
            yield Yield(resp)
    return run_gen_step_iter(gen_step, async_=async_)

