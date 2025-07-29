import asyncio
import numpy as np
from unittest.mock import patch, AsyncMock, MagicMock
from io import BytesIO

import pytest

from palabra_ai.internal.audio import (
    resample_pcm, write_to_disk, read_from_disk,
    convert_any_to_pcm16, pull_until_blocked
)


class TestAudio:
    def test_resample_pcm_variants(self):
        # Mono to mono
        data = b"\x00\x01" * 100
        result = resample_pcm(data, 16000, 48000, 1, 1)
        assert len(result) > len(data) * 2

        # Stereo to mono
        data = b"\x00\x01\x00\x02" * 50
        result = resample_pcm(data, 16000, 16000, 2, 1)
        assert len(result) == len(data) // 2

        # Odd samples
        data = b"\x00\x01\x00\x02"
        result = resample_pcm(data, 16000, 16000, 2, 1)
        assert len(result) == 2

        # 2D array
        data = np.array([[1, 2], [3, 4]], dtype=np.int16).tobytes()
        result = resample_pcm(data, 16000, 16000, 2, 1)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_write_to_disk(self):
        mock_file = AsyncMock()
        mock_file.write.return_value = 4

        with patch("palabra_ai.internal.audio.async_open") as mock_open:
            mock_open.return_value.__aenter__.return_value = mock_file

            result = await write_to_disk("test.wav", b"data")
            assert result == 4
            mock_file.write.assert_called_once_with(b"data")

    @pytest.mark.asyncio
    async def test_read_from_disk(self):
        mock_file = AsyncMock()
        mock_file.read.return_value = b"data"

        with patch("palabra_ai.internal.audio.async_open") as mock_open:
            mock_open.return_value.__aenter__.return_value = mock_file

            result = await read_from_disk("test.wav")
            assert result == b"data"

    @pytest.mark.asyncio
    async def test_disk_operations_cancelled(self):
        mock_file = AsyncMock()
        mock_file.write.side_effect = asyncio.CancelledError
        mock_file.read.side_effect = asyncio.CancelledError

        with patch("palabra_ai.internal.audio.async_open") as mock_open:
            mock_open.return_value.__aenter__.return_value = mock_file

            with pytest.raises(asyncio.CancelledError):
                await write_to_disk("test.wav", b"data")

            with pytest.raises(asyncio.CancelledError):
                await read_from_disk("test.wav")

    def test_convert_any_to_pcm16_error_paths(self, mock_av):
        mock_av.open.side_effect = Exception("Mock error")
        from av.error import FFmpegError
        mock_av.FFmpegError = FFmpegError

        with patch("palabra_ai.internal.audio.time.perf_counter", return_value=1.0):
            with pytest.raises(Exception):
                convert_any_to_pcm16(b"test", sample_rate=16000, layout="mono", normalize=True)

        # Without normalization
        with patch("palabra_ai.internal.audio.error"):
            with pytest.raises(Exception):
                convert_any_to_pcm16(b"test", normalize=False)

    def test_convert_any_to_pcm16_success(self, mock_av):
        # Setup complex mocks for success path
        mock_input = MagicMock()
        mock_output = MagicMock()

        mock_stream = MagicMock()
        mock_stream.format = MagicMock()
        mock_stream.format.name = "s16"
        mock_stream.rate = 16000
        mock_stream.layout = "mono"
        mock_stream.time_base = MagicMock()
        mock_stream.encode.return_value = []

        mock_av.open.side_effect = [mock_input, mock_output]
        mock_output.add_stream.return_value = mock_stream

        with patch("palabra_ai.internal.audio.Fraction", return_value=MagicMock()):
            mock_frame = MagicMock()
            mock_frame.samples = 100
            mock_frame.pts = 0
            mock_input.decode.return_value = [mock_frame]

            mock_resampler = MagicMock()
            mock_resampler.resample.return_value = [mock_frame]
            mock_av.AudioResampler.return_value = mock_resampler

            mock_av.AudioFormat.return_value = MagicMock()

            # Setup filter graph
            mock_graph = MagicMock()
            mock_buffer_node = MagicMock()
            mock_sink_node = MagicMock()

            # Mock FilterGraph that is imported at the top of audio.py
            mock_graph.add_abuffer.return_value = mock_buffer_node
            mock_graph.add.side_effect = [MagicMock(), MagicMock(), mock_sink_node]

            with patch("palabra_ai.internal.audio.pull_until_blocked", return_value=[mock_frame]):
                output_bytes = BytesIO()
                with patch("palabra_ai.internal.audio.BytesIO") as mock_bytesio:
                    mock_bytesio.side_effect = [BytesIO(b"test"), output_bytes]

                    # Mock the new error types
                    from av.error import BlockingIOError as AvBlockingIOError, EOFError as AvEOFError, FFmpegError

                    # Mock sink pull behavior - create instances of exceptions
                    mock_sink_node.pull.side_effect = [
                        mock_frame,
                        AvBlockingIOError(1, "EAGAIN", "test")
                    ]

                    # Mock buffer push behavior - create instances of exceptions
                    mock_buffer_node.push.side_effect = [None, AvEOFError(1, "EOF", "test")]

                    # Patch the imported error types in audio module
                    with patch("palabra_ai.internal.audio.AvBlockingIOError", AvBlockingIOError):
                        with patch("palabra_ai.internal.audio.AvEOFError", AvEOFError):
                            with patch("palabra_ai.internal.audio.FilterGraph", return_value=mock_graph):
                                with patch("palabra_ai.internal.audio.FFmpegError", FFmpegError):
                                    result = convert_any_to_pcm16(b"test", normalize=True)
                                    assert isinstance(result, bytes)

    def test_pull_until_blocked(self, mock_av):
        mock_graph = MagicMock()

        from av.error import BlockingIOError as AvBlockingIOError, FFmpegError

        # Test blocking IO error behavior - create instance of exception
        mock_graph.pull.side_effect = ["frame1", "frame2", AvBlockingIOError(1, "EAGAIN", "test")]

        with patch("palabra_ai.internal.audio.AvBlockingIOError", AvBlockingIOError):
            with patch("palabra_ai.internal.audio.FFmpegError", FFmpegError):
                result = pull_until_blocked(mock_graph)
                assert result == ["frame1", "frame2"]

                # Test other FFmpeg error - create instance of exception
                mock_graph.pull.side_effect = FFmpegError(1, "Generic error", "test")

                with pytest.raises(FFmpegError):
                    pull_until_blocked(mock_graph)
