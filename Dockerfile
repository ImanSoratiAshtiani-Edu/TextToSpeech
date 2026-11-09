FROM public.ecr.aws/deep-learning-containers/vllm@sha256:7e1f0b3cce437c5d857824de2c47716302143102ce18314acb70e3f9409a19d3
COPY scripts/patch_runner.py /tmp/kaspar_patch_runner.py
RUN python3 /tmp/kaspar_patch_runner.py
