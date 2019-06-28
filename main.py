import asyncio
import contextlib
import os
import sys
import tempfile
import zipfile

import boto3
from quart import Quart

BUCKET = 'folkol.com'

s3 = boto3.client('s3')
app = Quart(__name__)


def cached_etag(plug):
    """Returns the etag of the current version of <plug>, if any."""
    with contextlib.suppress(FileNotFoundError):
        with open(f'cache/{plug}/etag') as f:
            return f.read()


def download(plug, etag):
    """Downloads and extracts <plug> into a temp dir, and symlinks to it.

    N.b. Several requests might trigger the same download, but since os.rename
    is atomic -- at least within the same POSIX filesystem -- one of them will
    persist and the resulting symlink should point to an unspoiled plug.
    """
    print(f'>>> Updating {plug}')

    tmpdir = tempfile.mkdtemp(dir='cache')
    archive = f'{tmpdir}/{plug}.zip'
    s3.download_file(BUCKET, f'{plug}.zip', archive)
    with zipfile.ZipFile(archive, "r") as f:
        f.extractall(os.path.join(tmpdir, 'code'))

    with open(os.path.join(tmpdir, 'etag'), 'w') as f:
        f.write(etag)

    link_name = os.path.basename(tmpdir)
    os.symlink(link_name, link_name + '.lnk')
    os.rename(link_name + '.lnk', os.path.join('cache', plug))


@app.route('/exec/<plug>/<command>')
async def exec(plug, command):
    """Downloads zipped Python code from S3 and calls <command>."""
    head = s3.head_object(Bucket=BUCKET, Key=f'{plug}.zip')
    etag = head['ETag']
    if etag != cached_etag(plug):
        download(plug, etag)

    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        f'cache/{plug}/code/{command}.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    await proc.wait()  # Possible deadlock if the PIPE buffer is too small?

    if proc.returncode == 0:
        return await proc.stdout.read()
    else:
        return await proc.stderr.read()


if __name__ == '__main__':
    with contextlib.suppress(FileExistsError):
        os.mkdir('cache')
    app.run()
