# Packaging Journal

## Python Package

### What worked

* Installed the project locally using editable installation (`pip install -e .`).
* Successfully exposed the `pkg-inspector` command-line interface through the package entry point.
* Ran the test suite successfully using pytest.
* Verified that the tool could inspect its own repository and achieve a packaging readiness score of 100/100.

### What I learned

* A Python package is more than source code; it also includes metadata, licensing, documentation, tests, and distribution configuration.
* Entry points allow Python packages to expose executable CLI commands.
* Packaging quality depends on reproducibility and clear project structure as much as application functionality.
* A well-configured `pyproject.toml` acts as the central source of packaging metadata.

---

## Snapcraft

### What worked

* Created an Ubuntu 24.04 development environment using Multipass.
* Installed Snapcraft and configured the build environment.
* Built a Snap package: `pkg-inspector_0.1.0_arm64.snap`.
* Installed and tested the generated Snap locally.
* Added packaging metadata including license, contact information, source code repository, issue tracker, and project website.

### What broke

* The initial build failed because the virtual machine had insufficient disk space.
* Snapcraft reported YAML parsing errors after metadata updates.
* Multiple metadata validation warnings were raised because required packaging fields were missing.

### How I fixed it

* Recreated the Multipass virtual machine with a larger disk allocation (~20 GB).
* Used `cat -n snap/snapcraft.yaml` to locate YAML formatting and indentation issues.
* Added missing metadata fields and corrected configuration formatting.
* Rebuilt and reinstalled the Snap to verify the fixes.

### What I learned

* Snapcraft creates isolated build environments and requires sufficient storage for dependency downloads and build artifacts.
* Packaging configuration files are strict; even small YAML formatting mistakes can prevent builds from succeeding.
* Metadata is treated as a first-class component of software distribution.
* Snap confinement controls application access to system resources, and interfaces such as `home` must be declared explicitly.
* Building software is only part of packaging; describing, documenting, and securing the package are equally important.

---

## Rockcraft

### What worked

* Installed Rockcraft and built an OCI-compliant rock image.
* Generated `pkg-inspector_0.1.0_arm64.rock`.
* Imported the rock into Docker using Rockcraft's bundled `skopeo` utility.
* Verified that the generated container image was available through Docker.

### What broke

* The workflow was less familiar than Snapcraft because rocks are distributed as OCI container images rather than traditional application packages.
* Additional tooling was required to load and inspect the generated image.

### How I fixed it

* Installed Docker inside the Ubuntu VM.
* Used `rockcraft.skopeo` to copy the generated OCI archive into Docker's local image store.
* Verified the image using `docker images`.

### What I learned

* Rocks package applications as OCI container images rather than operating-system-level packages.
* Rockcraft focuses on containerized deployment scenarios and cloud-native environments.
* Container images include both the application and a base operating system layer, which significantly influences final image size.
* The packaging workflow differs from Snapcraft even though both tools originate from the same ecosystem.

---

## Debian Packaging

### What worked

* Installed Debian packaging tools including `debhelper`, `dh-python`, `devscripts`, and related build dependencies.
* Successfully built a Debian package using `dpkg-buildpackage`.
* Generated `pkg-inspector_0.1.0_all.deb`.
* Installed the package through APT and verified that the executable was available in `/usr/bin`.
* Confirmed that the packaged application functioned correctly after installation.

### What broke

* The initial build failed because required Python packaging dependencies were missing.
* Debian's build tooling required additional support packages for modern `pyproject.toml`-based builds.

### How I fixed it

* Installed the missing dependency `python3-all`.
* Installed `pybuild-plugin-pyproject` to support PEP 517/518 build workflows.
* Re-ran the build process after satisfying the required build dependencies.

### What I learned

* Debian packaging relies heavily on explicit build dependencies.
* Modern Python packaging standards must be integrated with Debian's build system through additional tooling.
* Debian packages install executables into standard system locations such as `/usr/bin`.
* Packaging systems often require understanding both the application and the conventions of the target distribution ecosystem.

---

## Key Takeaways

### Dependency Management

Each packaging system manages dependencies differently. Python packages rely on package metadata, Snaps bundle most dependencies, Rocks package applications inside OCI images, and Debian packages depend on system package relationships.

### Reproducibility

Reproducible builds require consistent configuration, explicit dependencies, version-controlled packaging files, and automated testing. Small configuration errors can prevent successful builds.

### Distribution Model Differences

* Python packages target Python developers.
* Snaps target end users across Linux distributions.
* Rocks target containerized and cloud-native environments.
* Debian packages integrate directly with operating system package managers.

### Developer Experience

Building the same application in multiple packaging formats highlighted that software distribution is a separate engineering discipline from software development. Packaging requires understanding build systems, metadata, dependency management, operating system conventions, security models, and release workflows.

### Overall Reflection

This project started as a simple Python CLI but evolved into a practical study of software packaging and distribution. Building, debugging, and validating the application across Python, Snap, Rock, and Debian ecosystems provided hands-on experience with real-world packaging workflows and reinforced the importance of reproducibility, automation, documentation, and maintainability in software engineering.
