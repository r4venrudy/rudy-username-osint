import asyncio
import unittest

from rudy_runtime.process_output import read_bounded


class ReadBoundedTests(unittest.IsolatedAsyncioTestCase):
    async def test_keeps_only_the_limit_and_stops_the_process_on_overflow(self):
        reader = asyncio.StreamReader()
        reader.feed_data(b"abcdefghij")
        reader.feed_eof()
        stopped = []

        output, truncated = await read_bounded(reader, 6, on_limit=lambda: stopped.append(True))

        self.assertEqual(output, b"abcdef")
        self.assertTrue(truncated)
        self.assertEqual(stopped, [True])

    async def test_drains_discarded_stderr_without_retaining_it(self):
        reader = asyncio.StreamReader()
        reader.feed_data(b"error details beyond the retained limit")
        reader.feed_eof()

        output, truncated = await read_bounded(reader, 5, drain=True)

        self.assertEqual(output, b"error")
        self.assertTrue(truncated)
        self.assertEqual(await reader.read(), b"")

    async def test_exact_limit_is_not_reported_as_truncated(self):
        reader = asyncio.StreamReader()
        reader.feed_data(b"exact")
        reader.feed_eof()

        output, truncated = await read_bounded(reader, 5)

        self.assertEqual(output, b"exact")
        self.assertFalse(truncated)

    async def test_invalid_limit_is_rejected(self):
        for limit in (0, -1, 1.5, True):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                await read_bounded(asyncio.StreamReader(), limit)


if __name__ == "__main__":
    unittest.main()
