# Packaging Journal

## Python package
Built and installed the project locally using editable install.

What worked:
- CLI installed successfully.
- Tests passed.
- The tool dogfoods itself and scored 100/100 after git initialization.

What I learned:
- Packaging quality depends on metadata, tests, documentation, CI, licensing, and reproducible structure.

## Snapcraft

What worked:
- Installed Ubuntu 24.04 using Multipass.
- Installed Snapcraft 9.0.0.
- Built a Snap package: pkg-inspector_0.1.0_arm64.snap.
- Fixed a YAML formatting issue in snapcraft.yaml.
- Increased VM disk from ~4GB to ~20GB after Snapcraft failed due to no space left on device.

What I learned:
- Snapcraft creates managed build environments and needs enough disk space.
- Snap packages require structured metadata such as summary, description, license, contact, source-code, and issues.
- YAML formatting matters because packaging configuration is strict.
- Strict confinement limits filesystem access; the home plug allows the CLI to inspect projects under the user's home directory.

What broke:

## Rockcraft
What worked:
What broke:
What I learned:

## Debian packaging
What worked:
What broke:
What I learned:

## Key takeaways
- Dependency management:
- Reproducibility:
- Distribution model differences:
- Developer experience: