# Portfolio development

Static HTML site; no Node build step is required. From the cloud workspace, start:

```sh
python3 -m http.server 8001 --bind 127.0.0.1 --directory /workspace
```

The project uses the `/1/` deployment path for legacy links. Validate via local HTTP requests under `/1/`; the cloud onboarding UI does not provide localhost previews.

## Added project evidence

- `projects/int302-image-processing.html`: combines the two INT302 labs with original reports and code-only MATLAB ZIP downloads. The browser interpolation example uses a generated pattern and is labelled as an explanatory illustration, not MATLAB experiment output.
- `projects/8051-motor-counter.html`: describes the supplied AT89C51 source and links a code-only Keil project. User-specific IDE settings, historical binaries and build logs are excluded. The page states the source/project clock mismatch and unverified hardware status.
- DailySense embeds the available 90-second excerpt and labels it accordingly.

MATLAB input datasets and third-party test images are not included in the new code-only archives. The original lab source is preserved, including its documented limitations. The new diagrams are explanatory portfolio graphics, not hardware photos or experimental results.

## Validation

Public baseline: homepage and eleven existing project HTML pages returned HTTP 200 from `https://shine574269.github.io/1/` on 28 October 2026. Local additions have not been published.

Chromium checked updated pages at widths 1440 and 390, including interpolation mode changes and actual muted playback of the DailySense excerpt. The embedded arithmetic example is checked at 0 and 570 pulses. Local link checks include the PDFs and new source ZIPs. These checks do not establish that the original MATLAB, Keil firmware or hardware runs.

The uploaded `MTFNN-CO-release2.zip` was confirmed by the owner to be the thesis code, but exceeds the tool's 32 MiB transfer limit and could not be inspected. No new thesis implementation or performance claims were added from that archive.

## Report-led project narratives

All nine featured detail pages now introduce the problem, personal contribution, method and evidence/limitations directly in HTML. Umbrella coursework (English) and later competition material (Chinese) are separated. The thesis chart/table are transcribed from the supplied experiment.log, with oracle-assisted selection stated explicitly. Original source, checkpoints and a matching environment are still needed for reproducibility; the uploaded README discusses Keras 3 while the dependency export pins 2.8. No new training run is claimed. The full DailySense 10:40 recording is still absent; only the 90-second excerpt is embedded.
