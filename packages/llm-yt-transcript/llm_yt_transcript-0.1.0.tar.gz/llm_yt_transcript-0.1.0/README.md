# llm-yt-transcript

[![PyPI](https://img.shields.io/pypi/v/llm-yt-transcript.svg)](https://pypi.org/project/llm-yt-transcript/)
[![Changelog](https://img.shields.io/github/v/release/kj-9/llm-yt-transcript?include_prereleases&label=changelog)](https://github.com/kj-9/llm-yt-transcript/releases)
[![Tests](https://github.com/kj-9/llm-yt-transcript/actions/workflows/test.yml/badge.svg)](https://github.com/kj-9/llm-yt-transcript/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/kj-9/llm-yt-transcript/blob/main/LICENSE)

`llm-yt-transcript` is a LLM plugin for YouTube transcripts as fragments. It leverages `yt-dlp` for downloading subtitles.

## Installation

```
llm install llm-yt-transcript
```


## Usage

### Download Subtitles

Use the `download_subtitles` function to download subtitles for a YouTube video:
```python
llm -f ytt:{youtube_video_url} 'summarize the transcript'
```

by default, it will download the English subtitles. You can specify the language using the `lang` parameter before the `:`. 
For example, to download Spanish subtitles, use:
```python
llm fragments show ytt:es:{youtube_video_url}
```

### Controlling Logging

You can control the logging behavior by setting the `LLM_YT_LOG` environment variable. For example:

```bash
export LLM_YT_LOG=debug
```

Supported log levels are:
- `debug`: Most verbose output, useful for debugging
- `info`: General information messages
- `warning`: Warning messages only (default)
- `error`: Error messages only
- `critical`: Critical error messages only

The default level is `warning`.

These log levels correspond directly to yt-dlp's internal logging system.


## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

```
cd llm-yt-transcript
uv sync --all-groups
```

Run the following command to run the tests:
```
uv run pytest
```
