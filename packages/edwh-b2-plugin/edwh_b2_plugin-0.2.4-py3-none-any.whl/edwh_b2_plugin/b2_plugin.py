import datetime
import itertools
import json
import re
import sys
import time
import typing
from dataclasses import InitVar, asdict, dataclass, field
from typing import Optional, cast

import edwh
import humanize
import tabulate
from edwh import task
from invoke import Context, Promise
from typing_extensions import Self


@dataclass
class Bucket:
    js: InitVar[dict] = None
    ctx: InitVar[Context] = None
    quick: InitVar[bool] = None
    name: str = field(init=False)
    size: int = field(init=False)
    hsize: str = field(init=False)
    visibility: str = field(init=False, repr=False)
    file_count: int = field(init=False)

    def __post_init__(self, js: dict, ctx: Context, quick: bool = False):
        self.name = js["bucketName"]
        self._ctx = ctx
        bucket_info = self._get_bucket(ctx, self.name, quick)
        self.visibility = bucket_info["bucketType"]
        self.size = bucket_info.get("totalSize", -1)
        self.file_count = bucket_info.get("fileCount", -1)
        self.hsize = humanize.naturalsize(self.size)

    @classmethod
    def _get_bucket(cls, ctx, name: str, quick: bool):
        return json.loads(
            ctx.run(
                f"b2 bucket get {'' if quick else '--show-size'} {name}",
                hide=True,
            ).stdout
        )

    @classmethod
    def find(cls, ctx: Context, name: str, quick: bool = False) -> Self:
        info = cls._get_bucket(ctx, name, quick)
        return Bucket(info, ctx, quick)


@task
def authenticate(c):
    try:
        # ensure bucketname is present, but don't use it right now.
        edwh.get_env_value("B2_ATTACHMENTS_BUCKETNAME")
        b2_keyid = edwh.get_env_value("B2_ATTACHMENTS_KEYID")
        b2_key = edwh.get_env_value("B2_ATTACHMENTS_KEY")
    except (FileNotFoundError, KeyError):
        print("Please run this command in an `omgeving` with a docker-compose.yml and B2_ settings!")
        exit(1)

    result = c.run(f"b2 account authorize {b2_keyid} {b2_key}", hide=True)
    if result.ok:
        print("done!")
    else:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)


@task(
    iterable=["bucket"],
    aliases=("bucket", "buckets"),
    help=dict(
        quick="Do not request sizes",
        bucket="(repeatable) bucket name or regexp to filter bucketnames against. ",
        purge="default: False; Purge files updated more than <purge> days ago. ",
        purge_filter="default: .*\\.(tgz|log|gz); Select only these files to purge (to prevent accidental removal) ",
    ),
)
def list_buckets(ctx, quick=False, bucket=None, purge=None, purge_filter=r".*\.(tgz|log|gz)"):
    all_buckets = {b["bucketName"]: b for b in json.loads(ctx.run("b2 bucket list --json", hide=True).stdout)}
    buckets_js = []
    if not bucket:
        buckets_js.extend(all_buckets.values())
    else:
        buckets_js.extend(
            value
            for bucket_name, value in all_buckets.items()
            if any(re.match(bucket_arg, bucket_name) for bucket_arg in bucket)
        )

    print("fetching details")
    buckets = []
    for idx, bucket in enumerate(buckets_js):
        print(f"loading bucket {idx}/{len(buckets_js)}")
        buckets.append(Bucket(bucket, ctx, quick))

    print(tabulate.tabulate([asdict(b) for b in buckets], headers="keys"))

    if not purge:
        return

    max_delta = datetime.timedelta(int(purge) if purge.isdigit() else 100)
    for idx, bucket in enumerate(buckets):
        print(f"Processing {idx}/{len(buckets)} buckets, name: {bucket.name}")
        _purge_bucket(ctx, bucket, max_delta, purge_filter)


def is_done(promise: Promise) -> bool:
    return promise.runner.process_is_finished


def join_all(promises: list[Promise], animate: Optional[typing.Sequence[str]] = None) -> bool:
    for idx in itertools.count():
        if all(is_done(_) for _ in promises):
            print(" " * 10, end="\r", file=sys.stderr)
            return all(_.join().ok for _ in promises)
        if animate:
            char = animate[idx % len(animate)] + " " * 10
            print(char, end="\r", flush=True, file=sys.stderr)
            time.sleep(0.5)


def _purge_bucket(
    ctx: Context,
    bucket: Bucket,
    max_delta: Optional[datetime.timedelta],
    purge_filter: str,
):
    name = bucket.name if bucket.name.startswith("b2://") else f"b2://{bucket.name}"
    file_list = json.loads(ctx.run(f"b2 ls --json {name} --recursive", hide=True).stdout)

    print(f"> Processing {len(file_list)} files.")
    now = datetime.datetime.now()
    to_remove_files = [
        file
        for file in file_list
        if (max_delta is None or (now - datetime.datetime.fromtimestamp(file["uploadTimestamp"] / 1000)) > max_delta)
        and re.match(purge_filter, file["fileName"])
    ]

    print(
        f"> Removing {humanize.naturalsize(sum(f['size'] for f in to_remove_files))} "
        f"in {len(to_remove_files)} of {len(file_list)} files."
    )
    if not edwh.confirm(f"Removing {len(to_remove_files)} files, are you sure? [yN] "):
        # stop
        return

    promises = []
    for idx, file in enumerate(to_remove_files, 1):
        print(f"Queueing {idx}/{len(to_remove_files)}: {file['fileName']}")
        promise = cast(
            Promise,
            ctx.run(
                f'b2 delete-file-version "{file["fileName"]}" "{file["fileId"]}"',
                hide=True,
                asynchronous=True,
            ),
        )
        promises.append(promise)

    if not join_all(promises, animate=(".", "..", "...")):
        print("Not all files could be deleted!")
    else:
        print("Done!")


@task()
def purge(ctx, bucket_name: str):
    bucket = Bucket.find(ctx, bucket_name, quick=True)

    _purge_bucket(ctx, bucket, None, ".+")
