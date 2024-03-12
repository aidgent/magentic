from typing import AsyncIterator

import pytest

from magentic import AsyncStreamedStr, StreamedStr
from magentic.streaming import (
    CachedAsyncIterable,
    CachedIterable,
    aiter_streamed_json_array,
    async_iter,
    atakewhile,
    iter_streamed_json_array,
)


@pytest.mark.asyncio
async def test_async_iter():
    output = async_iter(["Hello", " World"])
    assert isinstance(output, AsyncIterator)
    assert [chunk async for chunk in output] == ["Hello", " World"]


@pytest.mark.parametrize(
    ("predicate", "input", "expected"),
    [
        (lambda x: x < 3, async_iter(range(5)), [0, 1, 2]),
        (lambda x: x < 6, async_iter(range(5)), [0, 1, 2, 3, 4]),
        (lambda x: x < 0, async_iter(range(5)), []),
    ],
)
@pytest.mark.asyncio
async def test_atakewhile(predicate, input, expected):
    assert [x async for x in atakewhile(predicate, input)] == expected


iter_streamed_json_array_test_cases = [
    (["[]"], []),
    (['["He', 'llo", ', '"Wo', 'rld"]'], ['"Hello"', '"World"']),
    (["[1, 2, 3]"], ["1", "2", "3"]),
    (["[1, ", "2, 3]"], ["1", "2", "3"]),
    (['[{"a": 1}, {2: "b"}]'], ['{"a": 1}', '{2: "b"}']),
    (["{\n", '"value', '":', " [", "1, ", "2, 3", "]"], ["1", "2", "3"]),
]


@pytest.mark.parametrize(("input", "expected"), iter_streamed_json_array_test_cases)
def test_iter_streamed_json_array(input, expected):
    assert list(iter_streamed_json_array(iter(input))) == expected


@pytest.mark.parametrize(("input", "expected"), iter_streamed_json_array_test_cases)
@pytest.mark.asyncio
async def test_aiter_streamed_json_array(input, expected):
    assert [x async for x in aiter_streamed_json_array(async_iter(input))] == expected


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ([1, 2, 3], [1, 2, 3]),
        (iter([1, 2, 3]), [1, 2, 3]),
        (range(3), [0, 1, 2]),
    ],
)
def test_iter_cached_iterable(input, expected):
    cached_iterable = CachedIterable(input)
    assert list(cached_iterable) == list(expected)
    assert list(cached_iterable) == list(expected)


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ([1, 2, 3], [1, 2, 3]),
        (iter([1, 2, 3]), [1, 2, 3]),
        (range(3), [0, 1, 2]),
    ],
)
@pytest.mark.asyncio
async def test_aiter_cached_async_iterable(input, expected):
    cached_aiterable = CachedAsyncIterable(async_iter(input))
    assert [x async for x in cached_aiterable] == list(expected)
    assert [x async for x in cached_aiterable] == list(expected)


def test_streamed_str_iter():
    iter_chunks = iter(["Hello", " World"])
    streamed_str = StreamedStr(iter_chunks)
    assert list(streamed_str) == ["Hello", " World"]
    assert list(iter_chunks) == []  # iterator is exhausted
    assert list(streamed_str) == ["Hello", " World"]


def test_streamed_str_str():
    streamed_str = StreamedStr(["Hello", " World"])
    assert str(streamed_str) == "Hello World"


@pytest.mark.asyncio
async def test_async_streamed_str_iter():
    aiter_chunks = async_iter(["Hello", " World"])
    async_streamed_str = AsyncStreamedStr(aiter_chunks)
    assert [chunk async for chunk in async_streamed_str] == ["Hello", " World"]
    assert [chunk async for chunk in aiter_chunks] == []  # iterator is exhausted
    assert [chunk async for chunk in async_streamed_str] == ["Hello", " World"]


@pytest.mark.asyncio
async def test_async_streamed_str_to_string():
    async_streamed_str = AsyncStreamedStr(async_iter(["Hello", " World"]))
    assert await async_streamed_str.to_string() == "Hello World"
