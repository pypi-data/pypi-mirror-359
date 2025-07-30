# Contributing

First of all, thank you so much for contributing! 🎉 💯

This document contains guidelines on how to most effectively contribute within this repository.

If you are stuck, please feel free to ask any questions or ask for help.

## Code of conduct

This project is governed by our [code of conduct](code_of_conduct.md). By participating, you are expected to uphold this code.
Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to community leaders responsible for enforcement.
Please open a [new security advisory notice](https://github.com/WayScience/nviz/security/advisories/new) (using defaults or "n/a" where unable to fill in the form) to privately notify us of any incidents of this nature.

## Development

This project leverages development environments managed by [uv](https://docs.astral.sh/uv/).
We use [pytest](https://docs.pytest.org/) for testing and [GitHub actions](https://docs.github.com/en/actions) for automated tests.

### Development setup

Perform the following steps to setup a Python development environment.

1. [Install Python](https://www.python.org/downloads/) (we recommend using [`pyenv`](https://github.com/pyenv/pyenv) or similar)
1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Linting

Work added to this project is automatically checked using [pre-commit](https://pre-commit.com/) via [GitHub Actions](https://docs.github.com/en/actions).
Pre-commit can work alongside your local [git with git-hooks](https://pre-commit.com/index.html#3-install-the-git-hook-scripts)

After [installing pre-commit](https://pre-commit.com/#installation) within your development environment, the following command also can perform the same checks within your local development environment:

```sh
% pre-commit run --all-files
```

We use these same checks within our automated tests which are managed by [GitHub Actions workflows](https://docs.github.com/en/actions/using-workflows).
These automated tests generally must pass in order to merge work into this repository.

### Testing

Work added to this project is automatically tested using [pytest](https://docs.pytest.org/) via [GitHub Actions](https://docs.github.com/en/actions).
Pytest is installed through the uv environment for this project.
We recommend testing your work before opening pull requests with proposed changes.

You can run pytest on your work using the following example:

```sh
% uv run pytest
```

#### Tests which use Sage Bionetworks Synapse

[Sage Bionetworks Synapse](https://sagebionetworks.org/platform/synapse) is a suite of web services that enables researchers to aggregate, organize, analyze and share their scientific data, code and insights.
Synapse requires non-anonymous credentials to download data from the platform.
`nViz` uses Synapse to retrieve data for testing through a [Synapse Personal Access Token](https://help.synapse.org/docs/Managing-Your-Account.2055405596.html#ManagingYourAccount-PersonalAccessTokens).
You may set this token for use with `nViz` tests via `export SYNAPSE_AUTH_TOKEN=token_content_goes_here`.
If you do not set the environment variable, then the synapse-related tests will be skipped.

## Making changes to this repository

We welcome anyone to use [GitHub issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) (requires a GitHub login) or create [pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) (to directly make changes within this repository) to modify content found within this repository.

Specifically, there are several ways to suggest or make changes to this repository:

1. Open a GitHub issue: https://github.com/WayScience/nviz/issues
1. Create a pull request from a forked branch of the repository

### Creating a pull request

### Pull requests

After you’ve decided to contribute code and have written it up, please file a pull request.
We specifically follow a [forked pull request model](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork).
Please create a fork of this repository, clone the fork, and then create a new, feature-specific branch.
Once you make the necessary changes on this branch, you should file a pull request to incorporate your changes into this (fork upstream) repository.

The content and description of your pull request are directly related to the speed at which we are able to review, approve, and merge your contribution.
To ensure an efficient review process please perform the following steps:

1. Follow all instructions in the [pull request template](https://github.com/WayScience/nviz/blob/main/.github/PULL_REQUEST_TEMPLATE.md)
1. Triple check that your pull request is adding _one_ specific feature or additional group of content.
   Small, bite-sized pull requests move so much faster than large pull requests.
1. After submitting your pull request, ensure that your contribution passes all status checks (e.g. passes all tests)

Pull request review and approval is required by at least one project maintainer to merge.
We will do our best to review the code addition in a timely fashion.
Ensuring that you follow all steps above will increase our speed and ability to review.
We will check for accuracy, style, code coverage, and scope.

## Versioning

We use [`setuptools-scm`](https://github.com/pypa/setuptools-scm) to help version this software through [`PEP 440`](https://peps.python.org/pep-0440/) standards and [semver.org](https://semver.org/) standards.
Configuration for versioning is found within the `pyproject.toml` file.
All builds for packages include dynamic version data to help label distinct versions of the software.
`setuptools-scm` uses `git` tags to help distinguish version data.
We also use the `_version.py` file as a place to persist the version data for occaissions where the `git` history is unavailable or unwanted (this file is only present in package builds).
Versioning for the project is intended to align with GitHub Releases which provide `git` tag capabilities.

### Releases

We publish source code by using [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) available [here](https://github.com/wayscience/nviz/releases).
We publish a related Python package through the [Python Packaging Index (PyPI)](https://pypi.org/) available [here](https://pypi.org/project/nviz/).

#### Release Publishing Process

Several manual and automated steps are involved with publishing nviz releases.
See below for an overview of how this works.

Notes about [semantic version](https://en.wikipedia.org/wiki/Software_versioning#Semantic_versioning) (semver) specifications:
nviz version specifications are controlled through [`setuptools-scm`](https://github.com/pypa/setuptools-scm) to create version data based on [git tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging) and commits.
nviz release git tags are automatically applied through [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) and related inferred changes from [`release-drafter`](https://github.com/release-drafter/release-drafter).

1. Open a pull request and use a repository label for `release-<semver release type>` to label the pull request for visibility with [`release-drafter`](https://github.com/release-drafter/release-drafter) (for example, see [nviz#24](https://github.com/wayscience/nviz/pull/24) as a reference of a semver patch update).
1. On merging the pull request for the release, a [GitHub Actions workflow](https://docs.github.com/en/actions/using-workflows) defined in `draft-release.yml` leveraging [`release-drafter`](https://github.com/release-drafter/release-drafter) will draft a release for maintainers.
1. The draft GitHub release will include a version tag based on the GitHub PR label applied and `release-drafter`.
1. Make modifications as necessary to the draft GitHub release, then publish the release (the draft release does not normally need additional modifications).
1. On publishing the release, another GitHub Actions workflow defined in `publish-pypi.yml` will run to build and deploy the Python package to PyPI (utilizing the earlier modified `pyproject.toml` semantic version reference for labeling the release).

## Documentation

Documentation for this project is published using [Sphinx](https://www.sphinx-doc.org) with markdown and Jupyter notebook file compatibility provided by [myst-parser](https://myst-parser.readthedocs.io/en/latest/) and [myst-nb](https://myst-nb.readthedocs.io/en/latest/) to create a "documentation website" (also known as "docsite").
The docsite is hosted through [GitHub Pages](https://pages.github.com/) and deployed through automated [GitHub Actions](https://docs.github.com/en/actions) jobs which trigger on pushes to the main branch or the publishing of a new release on GitHub.
Documentation is versioned as outlined earlier sections covering versioning details to help ensure users are able to understand each release independently of one another.

It can sometimes be useful to test documentation builds locally before proposing changes within a pull request.
See below for some examples of how to build documentation locally.

```shell
# build single-version sphinx documentation
# (useful for troubleshooting potential issues)
uv run sphinx-build docs/src docs/build

# build multi-version sphinx documentation
# (used in production)
uv run sphinx-multiversion docs/src docs/build
```
