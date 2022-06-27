from pathlib import Path

from invoke import Collection
from invoke import task
from invoke.exceptions import Failure

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


@task
def scm_init(ctx):
    """Init scm repo (if required).

    Raises:
        Failure: .gitignore does not exist

    Returns:
        None
    """
    if not Path('.gitignore').is_file():
        raise Failure('.gitignore does not exist')

    if not Path('.git').is_dir():
        uri_remote = 'git@github.com:{}/{}.git'.format(GITHUB_USERNAME,
                                                       GITHUB_SLUG
                                                      )

        ctx.run('git init')
        ctx.run('git add .')
        ctx.run('git commit -m "new package from midwatch/cc-py3-pkg ({})"'.format(CC_VERSION))
        ctx.run('git branch -M main')
        ctx.run('git remote add origin {}'.format(uri_remote))
        ctx.run('git tag -a "v_0.0.0" -m "cookiecutter ref"')


@task
def scm_push(ctx):
    """Push all branches and tags to origin."""

    for branch in ('develop', 'main'):
        ctx.run('git push origin {}'.format(branch))

    ctx.run('git push --tags')


@task
def scm_status(ctx):
    """Show status of remote branches."""
    ctx.run('git for-each-ref --format="%(refname:short) %(upstream:track)" refs/heads')


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
def init(ctx):
    """Initialize freshly cloned repo"""
    scm_init(ctx)

    ctx.run('git flow init -d')
    ctx.run('git flow config set versiontagprefix v_')

    scm_push(ctx)


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

scm = Collection()
scm.add_task(scm_push, name="push")
scm.add_task(scm_status, name="status")

ns = Collection(build, clean, init, release)
ns.add_collection(scm, name="scm")
