from pathlib import Path

from invoke import Collection
from invoke import task
from invoke.exceptions import Failure

from mw_dry_invoke import git

GITHUB_USERNAME = "midwatch"
GITHUB_SLUG = "tgb-notebook"
CC_VERSION = "0.0.0"

RSYNC_HOST = "host"
RSYNC_USER = "user"
RSYNC_PATH_LOCAL = "build/www/"
RSYNC_PATH_REMOTE = "remote path"

TEMPLATE_ROOT = "project.d/templates"

ROOT_DIR = Path(__file__).parent


@task
def clean_build(ctx):
    """
    Clean up files from package building
    """
    ctx.run("rm -fr build/")



@task(pre=[clean_build])
def clean(ctx):
    """
    Runs all clean sub-tasks
    """
    pass


@task(clean)
def build(ctx):
    """
    Build html pages.
    """
    ctx.run('mkdir build')
    ctx.run('cp -r notebook build/rst')
    ctx.run(f'sphinx_notebook build notebook/ build/rst/index.rst')
    ctx.run('sphinx-build -b html build/rst build/www')


@task
def init_repo(ctx):
    """Initialize freshly cloned repo"""
    git.init(ctx)


@task(pre=[clean, build])
def release(ctx):
    """
    Build notebook and release to Google App Engine
    """
    args = [
        ctx['secrets']['pub']['user_name'],
        '--key-file={}'.format(Path.home() / ctx['secrets']['pub']['user_key']),
        '--project={}'.format(ctx['secrets']['pub']['project'])
        ]

    cmd = 'gcloud auth activate-service-account {}'.format(' '.join(args))
    ctx.run(cmd)
    ctx.run('gcloud app deploy')


ns = Collection(build, clean, init_repo, release)
ns.add_collection(git.collection, name="scm")
