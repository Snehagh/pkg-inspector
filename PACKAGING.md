# Packaging pkg-inspector three ways: snap, rock, and .deb

This document is both a **runbook** (how to actually build each artifact) and a
**comparison** of the three distribution models. The point of the exercise is
not the tool — it is to experience *why* packaging and distribution are hard,
first-hand.

> **Important:** run these builds yourself and keep your own notes on what
> broke. The authentic friction you hit is the material for your own write-up.
> Don't copy the prose below into an interview answer — use it as a map, then
> describe your *own* experience in your *own* words.

---

## 0. Environment

The craft tools (`snapcraft`, `rockcraft`) and Debian tooling are Linux-native.

**On macOS — use a Multipass VM:**

```bash
brew install --cask multipass
multipass launch 24.04 --name craft --cpus 2 --memory 4G --disk 20G
multipass mount "$PWD" craft:/home/ubuntu/pkg-inspector
multipass shell craft
```

**On native Ubuntu 24.04 — skip Multipass.** Either way, inside the Linux
environment install the toolchain. The craft tools use **LXD** as their
isolated build backend:

```bash
sudo snap install snapcraft --classic
sudo snap install rockcraft --classic
sudo snap install lxd
sudo lxd init --auto
sudo usermod -aG lxd "$USER" && newgrp lxd   # so you don't need sudo for lxc
```

---

## 1. Snap

```bash
cd pkg-inspector
snapcraft --use-lxd
# -> pkg-inspector_0.1.0_amd64.snap
sudo snap install pkg-inspector_0.1.0_amd64.snap --dangerous
pkg-inspector analyze ~/pkg-inspector
```

`--dangerous` is needed because the snap is locally built and unsigned.

**The lesson to internalise — confinement.** This snap uses `confinement:
strict` with the `home` interface. Try analysing a project *outside* your home
directory (e.g. `sudo cp -r pkg-inspector /opt/foo && pkg-inspector analyze
/opt/foo`). It will fail to see the files, because a strictly confined snap
cannot read arbitrary paths. This is the central snap tradeoff: **security
through confinement vs. the convenience of unrestricted filesystem access.**
The escape hatch (`confinement: classic`) removes the sandbox entirely and
requires manual review to publish — the wrong choice for a tool that only needs
to read a project directory.

---

## 2. Rock (OCI image)

```bash
rockcraft pack
# -> pkg-inspector_0.1.0_amd64.rock
# Load the OCI archive into the local Docker daemon (skopeo ships with rockcraft):
sudo rockcraft.skopeo --insecure-policy copy \
  oci-archive:pkg-inspector_0.1.0_amd64.rock docker-daemon:pkg-inspector:0.1.0
# Rocks use Pebble as the entrypoint; invoke the CLI via `exec`:
docker run --rm -v "$PWD":/project pkg-inspector:0.1.0 exec pkg-inspector analyze /project
```

**The lesson — the artifact model can mismatch the workload.** Rocks are
designed for **long-running services**, with Pebble as their init/entrypoint.
A one-shot CLI is an awkward fit: you don't get a clean `docker run image cmd`,
you go through Pebble's `exec`. That awkwardness is informative — it shows that
"package it as a container" is not free; the container model carries
assumptions (a service lifecycle, a layered Ubuntu base) that may not match
your software. Note also the **image size**: an Ubuntu-based rock is far larger
than the few KB of Python you wrote — the base layer dominates.

---

## 3. Debian package (.deb)

```bash
sudo apt update
sudo apt install -y build-essential debhelper dh-python devscripts
dpkg-buildpackage -us -uc -b
# -> ../pkg-inspector_0.1.0_all.deb
sudo apt install ../pkg-inspector_0.1.0_all.deb
pkg-inspector analyze ~/pkg-inspector
```

**The lessons.** (1) Debian packaging is **metadata-heavy**: `debian/control`,
`rules`, `changelog`, `copyright`, `source/format` — each with strict format
rules — before a single line of your code is involved. (2) This package uses
the `3.0 (native)` source format to keep the local build simple (no separate
upstream tarball). Real upstream software is normally **non-native** —
`3.0 (quilt)` — which separates your pristine upstream source from the Debian
packaging and requires an `orig.tar.gz`. (3) The `.deb` integrates with `apt`'s
dependency resolution against the *system* Python — unlike the snap and rock,
which bundle their own runtime. That is the crux of the next section.

---

## 4. The comparison

| Dimension | snap | rock (OCI) | .deb |
| --- | --- | --- | --- |
| Runtime model | bundled, confined | bundled in image | uses system libs |
| Dependency handling | self-contained | self-contained | resolved by `apt` |
| Isolation | strict sandbox | container | none |
| Update model | automatic, transactional, rollback | re-pull image | `apt upgrade` |
| Target | desktop / IoT / server | cloud / CI / K8s | a specific distro release |
| Artifact size | medium | large (base layer) | tiny |
| Main friction | confinement boundaries | service-shaped, base size | metadata + per-distro |

---

## 5. Synthesis — why distributing software reliably is hard

These are the durable insights the exercise surfaces. Re-derive them from your
own build notes; they map directly onto the assessment's question about the
challenges of distributing software across platforms.

1. **The dependency/ABI problem.** The same source must run against wildly
   different system libraries. A binary linked against one `glibc` may not run
   on an older one. The two strategies are *bundle everything* (snap, rock —
   bigger, isolated, reproducible) or *depend on the system* (.deb — small, but
   only works on the distro release it was built for). Every model is a
   different answer to this one question.
2. **Reproducibility.** Without pinned inputs and isolated builds, "it builds on
   my machine" is not distribution. The craft tools build in clean LXD
   containers precisely to avoid host contamination.
3. **Multi-architecture.** amd64 is not enough; arm64 matters for cloud and
   devices. All three configs here declare multiple platforms — and that
   multiplies the build and testing surface.
4. **The security/usability tradeoff.** Confinement (snap) and isolation
   (container) protect users but constrain what software can do — and that
   constraint surfaces as real bugs, like this tool not reading `/opt`.
5. **Update and rollback.** Pushing software is easy; pushing the *next* version
   safely, with a way back, is the hard part. Transactional updates exist
   because of this.
6. **Maintainer effort and the long tail.** Packaging the same software N ways
   for N ecosystems is enormous, repeated human effort. **This is the reason
   Canonical's Craft team exists** — tools like snapcraft, rockcraft and
   charmcraft absorb that complexity so a publisher writes one declarative
   `*.yaml` instead of mastering five packaging systems.
